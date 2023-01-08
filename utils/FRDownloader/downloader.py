import logging
import sys
import tempfile
from datetime import datetime
from multiprocessing import Pool
from typing import List

import arxiv
import pandas as pd
from nltk.tokenize import sent_tokenize
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from tqdm import tqdm

from utils.FRDownloader.common import verify_primary_topic, default_fr_dataframe, prepare_nltk

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
        fr_with_context = article_text[max([i - 1, 0]):min(i + 2, len(article_text))]
        if len(fr_with_context) > 1:
            results.append(".".join(fr_with_context))

    return results


def _get_publication_date(article: arxiv.Result) -> datetime:
    return article.published


def _get_tags(article: arxiv.Result):
    """
    Find keywords
    :param article:
    :return:
    """
    return None


def _get_title(article: arxiv.Result) -> str:
    return article.title


def _get_authors(article: arxiv.Result) -> List[str]:
    return article.authors


def _get_abstract(article: arxiv.Result) -> str:
    return article.summary


def _parse_result(result: arxiv.Result, ) -> pd.DataFrame:
    """

    :param result:
    :return: DataFrame containing row that should be appended to the results' database.
    """
    df = default_fr_dataframe()
    log.debug(result.title)
    fr = _get_further_research_sections(result)

    for section in fr:
        df.loc[len(df)] = [section,
                           _get_publication_date(result),
                           _get_tags(result),
                           _get_title(result),
                           _get_authors(result),
                           _get_abstract(result)]

    return df if len(df) > 0 else None


def get_results_batch(results_generator, batch_size=32):
    result_batch = []
    more_to_come = True

    while len(result_batch) < batch_size and (more_to_come := ((result := next(results_generator)) is not None)):
        result_batch.append(result)

    return result_batch, more_to_come


def create_database(target_row_count: int = 1000, primary_topic: str = 'cs.AI', checkpoint: int = 10,
                    filename: str = None, pararell_processes: int = 8) -> pd.DataFrame:
    """

    :param target_row_count:
    :param primary_topic: The focus of the articles. This has to match one of the categories in the arxiv
        category taxonomy (https://arxiv.org/category_taxonomy)
    :return:
    """
    if filename == None:
        filename = "trainint_data.{}.csv".format(primary_topic)
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
            articles_batch, more_to_come = get_results_batch(results_generator, batch_size=pararell_processes)

            for parsed_result in pool.map(_parse_result, articles_batch):
                if parsed_result is not None:
                    pbar.update(len(parsed_result))
                    df = pd.concat([df, parsed_result], ignore_index=True)
                    if len(df) % checkpoint == 0:
                        df.to_csv(filename)

    return df


if __name__ == "__main__":
    create_database(1000, 'cs.AI', )
