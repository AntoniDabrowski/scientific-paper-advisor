from datetime import datetime
from time import mktime
from typing import List

import arxiv
import pandas as pd

from utils.FRDownloader.common import verify_primary_topic, default_fr_dataframe


def _get_further_research_section(article: arxiv.Result):
    pass


def _get_publication_date(article: arxiv.Result) -> datetime:
    return datetime.fromtimestamp(mktime(article.published))


def _get_tags(article: arxiv.Result):
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

    df[0]['further research'] = _get_further_research_section(result)
    df[0]['publication date'] = _get_publication_date(result)
    df[0]['tags'] = _get_tags(result)
    df[0]['title'] = _get_title(result)
    df[0]['authors'] = _get_authors(result)
    df[0]['abstract'] = _get_abstract(result)

    return df


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

    while len(df) < num_articles and (result := client.results(search) is not None):
        if parsed_result := _parse_result(result) is not None:
            df.append(parsed_result)

    return df


if __name__ == "__main__":
    create_database(50, 'cs.AI')
