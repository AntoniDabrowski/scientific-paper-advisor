from data_loader import load_data, prepare_chunks
from doc2vec import doc2vec
from clustering import k_centroids
from dimensionality_reduction import dimensionality_reduction, PCA_vs_TSNE
from sentence_transformers import SentenceTransformer
import pandas as pd
import pickle
from tqdm.auto import tqdm
from os import listdir
from os.path import isfile, join
import json

mypath_input = '../utils/FRDownloader/results'
mypath_output = '../utils/FRDownloader'


def pipeline(path, embedding_model='sentence transformer', alg='PCA', cut_outliers=False, show_plot=False,
             plot_name='', dim=3, test=False):
    df, docs = load_data(path)
    if df.shape[0] < 3:
        return None
    article_ids, embeddings = doc2vec(docs, model=embedding_model)
    labels = k_centroids(embeddings, k=3)
    if test:
        PCA_vs_TSNE(embeddings, labels, docs, plot_name=plot_name)
    else:
        reduced_vectors, labels, model = dimensionality_reduction(embeddings, labels, docs, alg=alg,
                                                                  cut_outliers=cut_outliers, show_plot=show_plot,
                                                                  plot_name=plot_name, dim=dim)
        return reduced_vectors, labels, df, model


def pipeline_all_results(path):
    chunks_fr, chunks_ab = prepare_chunks(pd.read_csv(path))

    SentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')
    processed_DFs = []

    for category, df in tqdm(list(chunks_fr.items())):
        # Further research
        df = df.iloc[:350].copy()
        FR_list = df['further research'][df['further research'].notna()].tolist()
        if len(FR_list) < 3:
            print(f'FR: {category}')
            continue

        FR_embeddings = SentenceTransformerModel.encode(FR_list)
        FR_labels = k_centroids(FR_embeddings, k=3)

        reduced_vectors, _, FR_model = dimensionality_reduction(FR_embeddings, FR_labels,
                                                                {i: value for i, value in enumerate(FR_list)},
                                                                alg='PCA',
                                                                cut_outliers=False, show_plot=False,
                                                                plot_name=f'FR: {category} {len(FR_list)}')

        FR_labels_column = []
        FR_x = []
        FR_y = []
        FR_z = []
        i = 0
        for indicator in df['further research'].notna().tolist():
            if indicator:
                FR_labels_column.append(FR_labels[i])
                FR_x.append(reduced_vectors[i, 0])
                FR_y.append(reduced_vectors[i, 1])
                FR_z.append(reduced_vectors[i, 2])
                i += 1
            else:
                FR_labels_column.append(None)
                FR_x.append(None)
                FR_y.append(None)
                FR_z.append(None)
        df['label'] = FR_labels_column

        df['x'] = FR_x
        df['y'] = FR_y
        df['z'] = FR_z

        processed_DFs.append(df)

        with open(f'../utils/FRDownloader/all_results/FR_models/{category}.pickle', 'wb') as file:
            pickle.dump(FR_model, file)

        df.to_csv(f'../utils/FRDownloader/all_results/FR_results/{category}_processed.csv', index=False)

    # result = pd.concat(processed_DFs)
    # result.to_csv(f'../utils/FRDownloader/all_results/extended_search_list_processed_FR.csv', index=False)

    processed_DFs = []
    for category, df in tqdm(list(chunks_ab.items())):
        # Abstract
        df = df.iloc[:350].copy()
        AB_list = df['abstract'][df['abstract'].notna()].tolist()
        if len(AB_list) < 3:
            print(f'AB: {category}')
            continue

        AB_embeddings = SentenceTransformerModel.encode(AB_list)
        AB_labels = k_centroids(AB_embeddings, k=3)

        reduced_vectors, _, AB_model = dimensionality_reduction(AB_embeddings, AB_labels,
                                                                {i: value for i, value in enumerate(AB_list)},
                                                                alg='PCA',
                                                                cut_outliers=False, show_plot=False,
                                                                plot_name=f'AB: {category} {len(AB_list)}')

        AB_labels_column = []
        AB_x = []
        AB_y = []
        AB_z = []
        i = 0
        for indicator in df['abstract'].notna().tolist():
            if indicator:
                AB_labels_column.append(AB_labels[i])
                AB_x.append(reduced_vectors[i, 0])
                AB_y.append(reduced_vectors[i, 1])
                AB_z.append(reduced_vectors[i, 2])
                i += 1
            else:
                AB_labels_column.append(None)
                AB_x.append(None)
                AB_y.append(None)
                AB_z.append(None)
        df['label'] = AB_labels_column

        df['x'] = AB_x
        df['y'] = AB_y
        df['z'] = AB_z

        # Saving data
        processed_DFs.append(df)

        with open(f'../utils/FRDownloader/all_results/AB_models/{category}.pickle', 'wb') as file:
            pickle.dump(AB_model, file)

        df.to_csv(f'../utils/FRDownloader/all_results/AB_results/{category}_processed.csv', index=False)

    # result = pd.concat(processed_DFs)
    # result.to_csv(f'../utils/FRDownloader/all_results/extended_search_list_processed_AB.csv', index=False)


def get_all_files():
    all_files = [f for f in listdir(mypath_input) if
                 isfile(join(mypath_input, f)) and f not in ['mass_parsing.csv', 'mass_parsing.csv.processed.pickle']]
    return all_files


if __name__ == "__main__":
    maps = json.load(open('../extension/scripts/categories.json'))
    for i, file in tqdm(enumerate(get_all_files())):
        f = file.split('.')
        if maps.get(f'{f[0]}.{f[1]}',"") not in ["Optimization and Control","Robotics","Machine Learning"]:
            continue
        try:
            pipeline(f'{mypath_input}/{file}',
                     embedding_model='sentence transformer',
                     alg='PCA', cut_outliers=False, show_plot=True, plot_name=maps[f'{f[0]}.{f[1]}'], dim=2, test=True)
        except:
            pass
    # pipeline_all_results('../utils/FRDownloader/all_results/extended_search_list.csv')
    # Currently following categories has too few samples to perform on them clusterization
    # FR: q-bio.SC
    # FR: cs.GL
