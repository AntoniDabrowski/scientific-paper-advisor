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
    try:
        extracted_text = pdf.to_text()
        extracted_text = sent_tokenize(extracted_text)

        for i, sentence in enumerate(extracted_text):
            if contain_phrase(sentence):
                sentence_prefix = safe_list_get(extracted_text, i - 1, None)
                sentence_suffix = safe_list_get(extracted_text, i + 1, None)

                df.loc[len(df)] = [sentence,
                                   sentence_prefix,
                                   sentence_suffix,
                                   article_info.published,
                                   article_info.title,
                                   article_info.primary_category,
                                   article_info.categories,
                                   article_info.authors,
                                   article_info.summary]
    except Exception as e:
        log.debug("\nArticle {}, title {} can't be decoded".format(pdf.pdf_file, article_info.title))
        log.debug(str(e))

    return df if len(df) > 0 else None


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


def make_pdfs_into_fr_database(files: Union[Path, str],
                               output_file: Union[Path, str],
                               checkpoint: int = 10,
                               parallel_workers: int = 8,
                               chunksize: int = 10):
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


handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)
# TODO add argparsing
if __name__ == '__main__':
    make_pdfs_into_fr_database(
        files="/mnt/i/arxiv",
        output_file="results/mass_parsing.csv",
        parallel_workers=8
    )
