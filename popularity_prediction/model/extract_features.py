import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from lexical_features import character_level, sentence_level, POS_frequency
from semantic_features import dense_embedding_df

def process_title(title):
    vec_1, labels_1 = character_level(title)
    vec_2, labels_2 = POS_frequency(title)
    return vec_1 + vec_2, labels_1 + labels_2


def process_abstract(abstract):
    vec_1, labels_1 = character_level(abstract)
    vec_2, labels_2 = sentence_level(abstract)
    vec_3, labels_3 = POS_frequency(abstract)
    return vec_1 + vec_2 + vec_3, labels_1 + labels_2 + labels_3


def process_authors(authors):
    return [], []


def extract_features(record):
    title_embedding, title_column_names = process_title(record['title'])
    abstract_embedding, abstract_column_names = process_abstract(record['abstract'])
    authors_embedding, authors_column_names = process_authors(record['authors'])
    return title_embedding + abstract_embedding + authors_embedding, \
           title_column_names + abstract_column_names + authors_column_names


def extract_features_all(df):
    records = []
    for _, record in df.iterrows():
        embedding, labels = extract_features(record)
        records.append(embedding)
    lexical_embeddings_df = pd.DataFrame.from_records(records, columns=labels)
    semantic_embeddings_df = dense_embedding_df(df)
    embeddings_df = pd.concat([lexical_embeddings_df, semantic_embeddings_df], axis=1)
    embeddings_df['category'] = df['category'].copy()
    return embeddings_df


if __name__ == '__main__':
    df = pd.read_csv(open('semanticscholar_results_to_quantiles.csv', encoding='UTF-8'))
    # df = pd.read_csv(open('out.csv', encoding='UTF-8'))
    embeddings_df = extract_features_all(df)
    embeddings_df.to_csv('semanticscholar_results_embeddings.csv',index=False)
