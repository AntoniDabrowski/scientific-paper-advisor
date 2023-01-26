import argparse
import json
import logging
import sys
import os
from json import JSONDecodeError
from math import ceil
from time import sleep
from typing import List

import numpy as np
import pandas as pd
from semanticscholar import SemanticScholar
from tqdm import tqdm

sch = SemanticScholar(api_key="mS4BRJlnio5xzZlVPQLID3wHIciImI898MGXrRQg")
MAX_CHUNK_SIZE = 100

parser = argparse.ArgumentParser(description="Tool for collecting the further research suggestions "
                                             "from the arxiv articles. ")

parser.add_argument("-o", "--output",
                    help="Dictates how many records should the output database contain.",
                    required=True)
parser.add_argument('-f', '--file', nargs='+', help='<Required> Set flag', required=True)

parser.add_argument("-d", "--debug", action="store_true")

args = parser.parse_args()

log = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG if args.debug else logging.WARNING)
log.addHandler(handler)


def load_files_into_dataframe(file_list: List[str]) -> pd.DataFrame:
    result = None
    for filename in file_list:
        if result is None:
            result = pd.read_csv(filename)
        else:
            new_df = pd.read_csv(filename)
            result = pd.concat([result, new_df])

    return result


def get_articles_details(df_of_articles: pd.DataFrame, output_file:str):
    num_od_splits = ceil(len(df_of_articles) / MAX_CHUNK_SIZE)

    for df_chunk in tqdm(np.array_split(df_of_articles, num_od_splits)):
        ids_list = [f'CorpusId:{idx}' for idx in df_chunk['corpusid'].to_list()]
        paper_abstracts = sch.get_papers(ids_list, fields=['abstract'])

        df_chunk['abstract'] = [paper['abstract'] for paper in paper_abstracts]
        interesting_parts = df_chunk[['title', 'abstract', 'authors', 'publicationdate', 'year', 'citationcount']]
        interesting_parts = interesting_parts.loc[interesting_parts['abstract'].notnull()]

        authors = interesting_parts['authors'].values
        aux = []
        for idx in authors:
            try:
                aux.append(json.loads(idx.replace("'", '"')))
            except JSONDecodeError:
                aux.append([])

        authors = aux
        authors = ['_'.join([x['name'] for x in article]) for article in authors]
        interesting_parts['authors'] = authors

        interesting_parts.to_csv(output_file, mode='a', index=False, header=(not os.path.exists(output_file)))

        sleep(1)


if __name__ == '__main__':
    df = load_files_into_dataframe(args.file)
    get_articles_details(df, args.output)
