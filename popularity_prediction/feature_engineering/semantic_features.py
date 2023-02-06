import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

SentenceTransformer_loaded = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def dense_embedding(df):
    embedding_title = SentenceTransformer_loaded.encode(df['title'].tolist())
    embedding_abstract = SentenceTransformer_loaded.encode(df['abstract'].tolist())
    return np.hstack([embedding_title, embedding_abstract])

def dense_embedding_df(df):
    records = dense_embedding(df)
    labels = [f'sem_{i}_dense_title' for i in range(384)] + [f'sem_{i}_dense_abstract' for i in range(384)]
    return pd.DataFrame.from_records(records, columns=labels)

if __name__ == '__main__':
    df = pd.read_csv(open('semanticscholar_results_to_quantiles.csv', encoding='UTF-8'))
    # df = pd.read_csv(open('out.csv', encoding='UTF-8'))
    embeddings = dense_embedding(df)
    np.savetxt("dense_embeddings.csv", embeddings, delimiter=",")
