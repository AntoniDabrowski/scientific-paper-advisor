import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
SentenceTransformer('./all-MiniLM-L6-v2')

def dense_embedding(df):
    embedding_title = SentenceTransformer.encode(df['title'].tolist())
    embedding_abstract = SentenceTransformer.encode(df['abstract'].tolist())
    return np.vstack([embedding_title,embedding_abstract])

if __name__ == '__main__':
    # df = pd.read_csv(open('semanticscholar_results_to_quantiles.csv', encoding='UTF-8'))
    df = pd.read_csv(open('out.csv', encoding='UTF-8'))
    print(df.shape[0])
    embedding = dense_embedding(df)
    print(embedding.shape[0])