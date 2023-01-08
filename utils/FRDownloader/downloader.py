import logging
import os.path
import pickle
import sys
import tempfile
from multiprocessing import Pool

import arxiv
import pandas as pd
from nltk.tokenize import sent_tokenize
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from tqdm import tqdm

from utils.FRDownloader.common import verify_primary_topic, default_fr_dataframe, prepare_nltk, safe_list_get

prepare_nltk()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.WARNING)
log.addHandler(handler)


def _get_further_research_sections(article: arxiv.Result):
    results = []

    log.debug("Article url: {}".format(article.pdf_url))

    with tempfile.NamedTemporaryFile() as fp:
        article.download_pdf(filename=fp.name)
        try:
            article_text = extract_text(fp.name)
        except PDFSyntaxError:
            return results

    article_text = sent_tokenize(article_text)
    fr_idxs = [x for x, t in enumerate(article_text) if 'further research' in t.lower()]
    for i in fr_idxs:
        results.append((
            safe_list_get(article_text, i - 1, None),
            safe_list_get(article_text, i, None),
            safe_list_get(article_text, i + 1, None)
        ))

    return results


def _parse_result(result: arxiv.Result, ) -> (str, pd.DataFrame):
    """

    :param result:
    :return: DataFrame containing row that should be appended to the results' database.
    """
    df = default_fr_dataframe()
    log.debug(result.title)
    fr = _get_further_research_sections(result)

    for fr_section, fr_prefix, fr_suffix in fr:
        df.loc[len(df)] = [fr_section,
                           fr_prefix,
                           fr_suffix,
                           result.published,
                           result.title,
                           result.primary_category,
                           result.categories,
                           result.authors,
                           result.summary]

    return result.title, df if len(df) > 0 else None


def get_results_batch(results_generator, batch_size=32, articles_to_ignore=None):
    if articles_to_ignore is None:
        articles_to_ignore = set()

    result_batch = []
    more_to_come = True

    while len(result_batch) < batch_size \
            and (more_to_come := ((result := next(results_generator)) is not None)):
        if result.title not in articles_to_ignore:
            result_batch.append(result)

    return result_batch, more_to_come


def create_database(target_row_count: int = 1000,
                    primary_topic: str = 'cs.AI',
                    checkpoint: int = 10,
                    filename: str = None,
                    pararell_processes: int = 8) -> pd.DataFrame:
    """

    :param target_row_count:
    :param primary_topic: The focus of the articles. This has to match one of the categories in the arxiv
        category taxonomy (https://arxiv.org/category_taxonomy)
    :return:
    """
    if filename is None:
        filename = "training_data.{}.csv".format(primary_topic)

    file_no_fr = "{}_no_fr.pickle".format(primary_topic)
    if os.path.exists(file_no_fr):
        with open(file_no_fr, 'rb') as fr_set:
            no_fr_set = pickle.load(fr_set)
    else:
        no_fr_set = set()

    verify_primary_topic()

    search = arxiv.Search(
        query="cat:{primary_topic}".format(primary_topic=primary_topic),
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    df = default_fr_dataframe()
    more_to_come = True
    client = arxiv.Client()

    results_generator = client.results(search)

    with tqdm(total=target_row_count) as pbar, Pool(processes=pararell_processes) as pool:
        while len(df) < target_row_count and more_to_come:
            articles_batch, more_to_come = get_results_batch(results_generator,
                                                             batch_size=pararell_processes,
                                                             articles_to_ignore=no_fr_set)

            for article_id, parsed_result in pool.map(_parse_result, articles_batch):
                if parsed_result is not None:
                    pbar.update(len(parsed_result))
                    df = pd.concat([df, parsed_result], ignore_index=True)
                    if len(df) % checkpoint == 0:
                        df.to_csv(filename)
                else:
                    no_fr_set.add(article_id)
                    if len(no_fr_set) % checkpoint == 0:
                        with open(file_no_fr, 'wb') as fr_set:
                            pickle.dump(no_fr_set, fr_set)

    return df


if __name__ == "__main__":
    create_database(1000, 'cs.AI')
