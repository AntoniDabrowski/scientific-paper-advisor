import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from lexical_features import character_level, sentence_level, POS_frequency, POS_bigrams_frequency, CSS_vector
from side_info_features import authors_value, venue_value, is_open_access_value, journal_value
from semantic_features import dense_embedding_df
from tqdm.auto import tqdm


def merge_lists(*args):
    vectors = []
    labels = []
    for v, l in args:
        vectors += v
        labels += l
    return vectors, labels


def process_title(title):
    return merge_lists(character_level(title),
                       POS_frequency(title),
                       CSS_vector(title),
                       POS_bigrams_frequency(title))


def process_abstract(abstract):
    return merge_lists(character_level(abstract),
                   sentence_level(abstract),
                   POS_frequency(abstract),
                   CSS_vector(abstract),
                   POS_bigrams_frequency(abstract))

def process_side_information(record):
    return merge_lists(authors_value(record['authors']),
                       venue_value(record['venue']),
                       is_open_access_value(record['isopenaccess']),
                       journal_value(record['journal']))


def extract_features(record):
    return merge_lists(process_title(record['title']),
                       process_abstract(record['abstract']),
                       process_side_information(record))


def extract_features_all(df):
    records = []
    pbar = tqdm(total=df.shape[0])
    for _, record in df.iterrows():
        pbar.update(1)
        embedding, labels = extract_features(record)
        records.append(embedding)
    pbar.close()
    lexical_embeddings_df = pd.DataFrame.from_records(records, columns=labels)
    semantic_embeddings_df = dense_embedding_df(df)
    embeddings_df = pd.concat([lexical_embeddings_df, semantic_embeddings_df], axis=1)
    embeddings_df['category'] = df['category'].copy()
    return embeddings_df


if __name__ == '__main__':
    df = pd.read_csv(open('../data/edition_2/semanticscholar_results2_quantiles.csv', encoding='UTF-8'))
    embeddings_df = extract_features_all(df)
    embeddings_df.to_csv('../data/edition_2/semanticscholar_results2_embeddings.csv', index=False)
