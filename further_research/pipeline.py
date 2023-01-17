from data_loader import load_data
from doc2vec import doc2vec
from clustering import k_centroids
from dimensionality_reduction import dimensionality_reduction


def pipeline(path, embedding_model='sentence transformer', alg='PCA', cut_outliers=False, show_plot=False,
             plot_name=''):
    df, docs = load_data(path)
    if df.shape[0] < 3:
        return None
    article_ids, embeddings = doc2vec(docs, model=embedding_model)
    labels = k_centroids(embeddings, k=3)
    reduced_vectors, labels, model = dimensionality_reduction(embeddings, labels, docs, alg=alg,
                                                              cut_outliers=cut_outliers, show_plot=show_plot,
                                                              plot_name=plot_name)
    return reduced_vectors, labels, df, model


if __name__ == "__main__":
    pipeline('./sample_data/training_data.cs.AI.csv',
             embedding_model='sentence transformer',
             alg='PCA', cut_outliers=False)
