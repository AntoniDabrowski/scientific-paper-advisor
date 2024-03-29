import argparse
import logging
import os.path
import pickle
import sys
import time
from multiprocessing import Pool, Semaphore, Manager
from pathlib import Path
from typing import Union, Set, List, Dict

import arxiv
import pandas as pd
from nltk import sent_tokenize
from pdftextract import XPdf
from tqdm import tqdm

from utils.FRDownloader.common import default_fr_dataframe, prepare_nltk, contain_phrase, safe_list_get, chunks

prepare_nltk()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def _get_files_list(files: Union[Path, str],
                    files_to_ignore: Set[Union[Path, str]]):
    if isinstance(files, str):
        files = Path(files)

    files_list = []

    if os.path.isfile(files):
        files_list = [files]
    else:
        for root_dir, _, file_names in os.walk(files):
            files_list += [Path(os.path.join(root_dir, file_name)) for file_name in file_names
                           if file_name.endswith('.pdf')
                           and Path(os.path.join(root_dir, file_name)) not in files_to_ignore]

    return files_list


def get_article_info(id_list: Union[str, List[str]],
                     semaphore: Semaphore = None) -> Dict[str, arxiv.Result]:
    """
    Find information about an article from the arxiv api based on the title
    :param semaphore:
    :param id_list: ID of the article
    :return: Result of the search
    """
    result = {}
    if semaphore is not None:
        semaphore.acquire()

    if isinstance(id_list, str):
        id_list = [id_list]

    arxiv_api_results = arxiv.Search(id_list=id_list).results()
    for arxiv_result in arxiv_api_results:
        result[arxiv_result.entry_id.split('/')[-1]] = arxiv_result

    time.sleep(1)  # Waiting to make sure we are abiding by the arxiv API rules

    if semaphore is not None:
        semaphore.release()

    return result


def _parse_pdf(pdf: XPdf, article_info: arxiv.Result) -> Union[pd.DataFrame, None]:
    df = default_fr_dataframe()
    fr_sentence = None
    fr_sentence_prefix = None
    fr_sentence_suffix = None

    try:
        extracted_text = pdf.to_text()
        extracted_text = sent_tokenize(extracted_text)

        for i, sentence in enumerate(extracted_text):
            if contain_phrase(sentence):
                fr_sentence = sentence
                fr_sentence_prefix = safe_list_get(extracted_text, i - 1, None)
                fr_sentence_suffix = safe_list_get(extracted_text, i + 1, None)

    except Exception as e:
        log.debug("\nArticle {}, title {} can't be decoded".format(pdf.pdf_file, article_info.title))
        log.debug(str(e))

    df.loc[0] = [fr_sentence,
                 fr_sentence_prefix,
                 fr_sentence_suffix,
                 article_info.published,
                 article_info.title,
                 article_info.primary_category,
                 article_info.categories,
                 article_info.authors,
                 article_info.summary,
                 article_info.pdf_url]

    return df


def _parse_files(files: List[Union[str, Path]],
                 semaphore: Semaphore = None) -> (List[Union[str, Path]], List[pd.DataFrame]):
    results = []
    pdfs = [XPdf(file) for file in files]
    arxiv_ids = [os.path.basename(file).split('.pdf')[0] for file in files]

    # We are getting arxiv infor for the whole batch at the same time to save up on the number of queries
    arxiv_info = get_article_info(arxiv_ids, semaphore)

    for pdf, arx_id in zip(pdfs, arxiv_ids):
        article_info = arxiv_info.get(arx_id, None)
        # None here means article wasn't found and we skip
        if article_info is not None:
            result = _parse_pdf(pdf, article_info)
            # None as a result means no interesting phrases were found.
            if result is not None:
                results.append(result)

    return files, results


def _save_progress(output_file_path, processed_files_path, curr_dataset: pd.DataFrame, processed_files):
    curr_dataset.to_csv(output_file_path)
    with open(processed_files_path, 'wb') as processed_files_pickle:
        pickle.dump(processed_files, processed_files_pickle)


def _load_progress(result_path):
    processed_set_path = "{}.processed.pickle".format(result_path)
    processed_files = set()

    if not os.path.exists(result_path):
        return default_fr_dataframe(), processed_files, processed_set_path

    df = pd.read_csv(result_path)

    if os.path.exists(processed_set_path):
        with open(processed_set_path, 'rb') as processed_files_pickle:
            processed_files = pickle.load(processed_files_pickle)

    return df, processed_files, processed_set_path


def _create_batch_for_workers(num_workers, chunks_generator, semaphore):
    return [(next(chunks_generator), semaphore) for _ in range(num_workers)]


def purge_unnamed_columns(df) -> pd.DataFrame:
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df


def dataframe_category_split(df: pd.DataFrame,
                             output_file: str = None) -> List[pd.DataFrame]:
    groups = df.groupby(['primary category'])

    for name, group in groups:
        group.to_csv("{}/{}.{}".format(os.path.dirname(output_file), name, os.path.basename(output_file)))

    return groups


def make_pdfs_into_fr_database(files: Union[Path, str],
                               output_file: Union[Path, str],
                               checkpoint: int = 10,
                               parallel_workers: int = 8,
                               chunksize: int = 10,
                               split_by_category=False) -> Union[pd.DataFrame, List[pd.DataFrame]]:
    # Load progress done so far
    df, processed_files, processed_set_path = _load_progress(output_file)

    files = _get_files_list(files, files_to_ignore=processed_files)
    total_iterations = round(len(files) / chunksize)
    chunks_generator = chunks(files, chunksize)
    more_to_come = True

    with tqdm(total=total_iterations) as pbar, Pool(processes=parallel_workers) as pool, Manager() as manager:
        arxiv_semaphore = manager.Semaphore(4)
        while more_to_come:
            try:
                articles_batch = _create_batch_for_workers(num_workers=parallel_workers,
                                                           chunks_generator=chunks_generator,
                                                           semaphore=arxiv_semaphore)

                for parsed_files, parsed_result in pool.starmap(_parse_files, articles_batch):
                    # Update database and processed files set with results
                    if parsed_result:
                        df = pd.concat([df] + parsed_result, ignore_index=True)
                    processed_files.update(parsed_files)

                    pbar.update()
                    if pbar.n % checkpoint == 0:
                        _save_progress(output_file_path=output_file,
                                       processed_files_path=processed_set_path,
                                       curr_dataset=df,
                                       processed_files=processed_files)
            except StopIteration:
                more_to_come = False

    df = purge_unnamed_columns(df)

    _save_progress(output_file_path=output_file,
                   processed_files_path=processed_set_path,
                   curr_dataset=df,
                   processed_files=processed_files)

    if split_by_category:
        dataframe_category_split(df, output_file)

    return df


parser = argparse.ArgumentParser(description="Tool for parsing pdf articles into a database of further "
                                             "research topics.")

parser.add_argument("-d", "--source-directory",
                    help="Dictates from where the pdfs should be taken.",
                    required=True)
parser.add_argument("-c", "--checkpoint",
                    default=10,
                    help="Number of chunks after which the result will be saved..",
                    type=int)
parser.add_argument("-ch", "--chunksize",
                    default=10,
                    help="Number of the articles given to the worker in a single chunk.",
                    type=int)
parser.add_argument("-pp", "--parallel-processes",
                    default=2,
                    help="Numbers of parallel workers to use for parsing of the articles.",
                    type=int)
parser.add_argument("--debug", action="store_true")
parser.add_argument("-o", "--output-file",
                    help="Name of the output file. This will be a csv file."
                         "If this files already exist and is of csv format the script will try to append "
                         "the results to it, to allow continuation of interrupted processes.",
                    required=True)
parser.add_argument("-s", "--category-split", action="store_true", help="Creates a set of csv files that are the "
                                                                        "result of splitting the output file by "
                                                                        "primary categories.")

args = parser.parse_args()

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG if args.debug else logging.WARNING)
log.addHandler(handler)

if __name__ == '__main__':
    make_pdfs_into_fr_database(
        files=args.source_directory,
        output_file=args.output_file,
        parallel_workers=args.parallel_processes,
        chunksize=args.chunksize,
        checkpoint=args.checkpoint,
        split_by_category=args.category_split
    )
