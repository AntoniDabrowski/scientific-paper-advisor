from data_loader import load_data
from doc2vec import doc2vec
from clustering import k_centroids
from dimensionality_reduction import dimensionality_reduction


def pipeline(path, embedding_model='document transformer', alg='PCA', cut_outliers=False):
    df, docs = load_data(path)
    article_ids, embeddings = doc2vec(docs, model=embedding_model)
    labels = k_centroids(embeddings, k=3)
    dimensionality_reduction(embeddings, labels, docs, alg=alg, cut_outliers=cut_outliers)


if __name__ == "__main__":
    pipeline('./sample_data/training_data.cs.AI.csv',
             embedding_model='document transformer',
             alg='PCA', cut_outliers=False)
