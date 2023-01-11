from data_loader import load_data
from doc2vec import doc2vec
from clustering import k_centroids
from dimensionality_reduction import dimensionality_reduction


def pipeline(path):
    df, docs = load_data(path)
    article_ids, embeddings = doc2vec(docs)
    labels = k_centroids(embeddings, k=3)
    dimensionality_reduction(embeddings, labels, docs)


if __name__ == "__main__":
    pipeline('./sample_data/training_data.cs.AI.csv')
