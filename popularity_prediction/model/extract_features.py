import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def process_title(title):
    return [], []

def process_abstract(abstract):
    return [], []

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
        embedding = extract_features(record)
        records.append(embedding)
    return records


if __name__ == '__main__':
    df = pd.read_csv(open('semanticscholar_results_to_quantiles.csv', encoding='UTF-8'))
    extract_features_all(df)
