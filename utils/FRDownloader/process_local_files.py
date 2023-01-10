import os.path
import pickle
import time
from itertools import repeat
from multiprocessing import Pool, Semaphore
from pathlib import Path
from typing import Union, Set, List, Dict

import arxiv
import pandas as pd
from nltk import sent_tokenize
from pdftextract import XPdf
from tqdm import tqdm

from utils.FRDownloader.common import default_fr_dataframe, prepare_nltk, contain_phrase, safe_list_get

prepare_nltk()


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


def get_article_info(title: Union[str, List[str]],
                     semaphore: Semaphore = None) -> Dict[str, arxiv.Result]:
    """
    Find information about an article from the arxiv api based on the title
    :param semaphore:
    :param title: Title of the article
    :return: Result of the search
    """
    result = {}
    if semaphore is not None:
        semaphore.acquire()

    if isinstance(title, str):
        title = [title]

    query = "+OR+".join(["ti:{}".format(t) for t in title])
    arxiv_api_results = arxiv.Search(query=query).results()
    for arxiv_result in arxiv_api_results:
        result[arxiv_result.title] = arxiv_result

    time.sleep(1)  # Waiting to make sure we are abiding by the arxiv API rules

    if semaphore is not None:
        semaphore.release()

    return result


def _parse_pdf(pdf: XPdf, article_info: arxiv.Result) -> Union[pd.DataFrame, None]:
    df = default_fr_dataframe()
    extracted_text = sent_tokenize(pdf.to_text())

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

    return df if len(df) > 0 else None


def _parse_files(files: List[Union[str, Path]],
                 semaphore: Semaphore = None) -> (List[Union[str, Path]], List[pd.DataFrame]):
    results = []
    pdfs = [XPdf(file) for file in files]

    # We are getting arxiv infor for the whole batch at the same time to save up on the number of queries
    arxiv_info = get_article_info([pdf.info['Title'] for pdf in pdfs], semaphore)

    for pdf in pdfs:
        article_info = arxiv_info.get(pdf.info['Title'], None)
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


def make_pdfs_into_fr_database(files: Union[Path, str],
                               output_file: Union[Path, str],
                               checkpoint: int = 10,
                               parallel_workers: int = 2,
                               chunksize: int = 10):
    arxiv_semaphore = Semaphore(4)  # Make 4 requests max each second

    # Load progress done so far
    df, processed_files, processed_set_path = _load_progress(output_file)

    files = _get_files_list(files, files_to_ignore=processed_files)
    total_iterations = len(files) / chunksize

    with tqdm(total=total_iterations) as pbar, Pool(processes=parallel_workers) as pool:
        for parsed_files, parsed_result in pool.starmap(_parse_files,
                                                        zip(files, repeat([arxiv_semaphore])),
                                                        chunksize=chunksize):

            # Update database and processed files set with results
            df = pd.concat([df] + parsed_result, ignore_index=True)
            processed_files.update(parsed_files)

            pbar.update()
            if pbar.n % checkpoint == 0:
                _save_progress(output_file_path=output_file,
                               processed_files_path=processed_set_path,
                               curr_dataset=df,
                               processed_files=processed_files)


if __name__ == '__main__':
    pass
