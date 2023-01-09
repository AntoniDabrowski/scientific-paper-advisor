import logging
import os.path
import pickle
import sys
import tempfile
import time
from multiprocessing import Pool
from multiprocessing.pool import MaybeEncodingError

import arxiv
import pandas
import pandas as pd
import requests
from arxiv import UnexpectedEmptyPageError
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
        url = article.pdf_url.replace('arxiv.org', 'export.arxiv.org')
        try:
            response = requests.get(url)
            fp.write(response.content)
            article_text = extract_text(fp.name)
        except PDFSyntaxError:
            return results
        except Exception as e:
            log.error(str(e))
            log.error("Error occurred while parsing {}".format(article.title))
            log.error("URL of the article {}".format(url))
            return "Parsing error"

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
    try:
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

        return df if len(df) > 0 else result.title
    except Exception as e:
        log.error(str(e))
        log.error("Error occurred while parsing {}".format(result.title))
        return "Parsing error"


def get_results_batch(results_generator, batch_size=32, articles_to_ignore=None, already_processed=[]):
    if articles_to_ignore is None:
        articles_to_ignore = set()

    result_batch = []
    more_to_come = True

    while len(result_batch) < batch_size and more_to_come:
        try:
            more_to_come = ((result := next(results_generator)) is not None)
            if result.title not in articles_to_ignore and result.title not in already_processed:
                result_batch.append(result)
        except UnexpectedEmptyPageError as e:
            log.error(str(e))
            time.sleep(10)
            continue

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
    verify_primary_topic(primary_topic)

    if filename is None:
        filename = "training_data.{}.csv".format(primary_topic)

    file_no_fr = "{}_no_fr.pickle".format(primary_topic)
    if os.path.exists(file_no_fr):
        with open(file_no_fr, 'rb') as fr_set:
            no_fr_set = pickle.load(fr_set)
    else:
        no_fr_set = set()

    search = arxiv.Search(
        query="cat:{primary_topic}".format(primary_topic=primary_topic),
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    print(search.results())

    if not os.path.exists(filename):
        df = default_fr_dataframe()
    else:
        df = pandas.read_csv(filename)

    more_to_come = True
    client = arxiv.Client()

    results_generator = client.results(search)

    with tqdm(total=target_row_count-len(df)) as pbar, Pool(processes=pararell_processes) as pool:
        while len(df) < target_row_count and more_to_come:
            articles_batch, more_to_come = get_results_batch(results_generator,
                                                             batch_size=pararell_processes,
                                                             articles_to_ignore=no_fr_set,
                                                             already_processed=df['title'].values)
            try:
                for parsed_result in pool.map(_parse_result, articles_batch):
                    # article_id, parsed_result = result_tuple
                    if not isinstance(parsed_result, str):
                        pbar.update(len(parsed_result))
                        df = pd.concat([df, parsed_result], ignore_index=True)
                        if len(df) % checkpoint == 0:
                            df.to_csv(filename)
                    else:
                        no_fr_set.add(parsed_result)
                        if len(no_fr_set) % checkpoint == 0:
                            with open(file_no_fr, 'wb') as fr_set_file:
                                pickle.dump(no_fr_set, fr_set_file)
            except MaybeEncodingError:
                log.error("Some of those articles caused errors.")
                for article in articles_batch:
                    log.error(article.title)

    return df


if __name__ == "__main__":
    create_database(1000, 'cs.AI')
