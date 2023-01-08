import logging
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List

import arxiv
import pandas as pd
from nltk.tokenize import sent_tokenize
from science_parse_api.api import parse_pdf
from tqdm import tqdm

from utils.FRDownloader.common import verify_primary_topic, default_fr_dataframe, prepare_nltk

prepare_nltk()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)


def _get_further_research_sections(article: arxiv.Result):
    host = 'http://127.0.0.1'
    port = '8080'
    results = []

    log.debug("Article url: {}".format(article.pdf_url))

    with tempfile.NamedTemporaryFile() as fp:
        article.download_pdf(filename=fp.name)
        output_dict = parse_pdf(host, Path(fp.name), port=port)

    # TODO if section is called further research, get the whole section

    for section in output_dict['sections']:
        section_text = sent_tokenize(section['text'])
        fr_idxs = [x for x, t in enumerate(section_text) if 'further research' in t.lower()]
        for i in fr_idxs:
            fr_with_context = section_text[max([i - 1, 0]):min(i + 2, len(section_text))]
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


def _parse_result(result: arxiv.Result) -> pd.DataFrame:
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


def create_database(num_articles: int, primary_topic: str) -> pd.DataFrame:
    """

    :param num_articles:
    :param primary_topic: The focus of the articles. This has to match one of the categories in the arxiv
        category taxonomy (https://arxiv.org/category_taxonomy)
    :return:
    """
    verify_primary_topic()

    search = arxiv.Search(
        query="cat:{primary_topic}".format(primary_topic=primary_topic)
    )

    df = default_fr_dataframe()

    client = arxiv.Client()
    results_generator = client.results(search)

    with tqdm(total=num_articles) as pbar:
        while len(df) < num_articles and (result := next(results_generator)) is not None:
            if (parsed_result := _parse_result(result)) is not None:
                pbar.update(len(parsed_result))
                df = pd.concat([df, parsed_result], ignore_index=True)

    return df


if __name__ == "__main__":
    create_database(50, 'cs.AI')
