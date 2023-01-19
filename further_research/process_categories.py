from os import listdir
from os.path import isfile, join
from tqdm.auto import tqdm
from pipeline import pipeline
import pickle

mypath_input = '../utils/FRDownloader/results'
mypath_output = '../utils/FRDownloader'


def get_all_files():
    all_files = [f for f in listdir(mypath_input) if
                 isfile(join(mypath_input, f)) and f not in ['mass_parsing.csv', 'mass_parsing.csv.processed.pickle']]
    return all_files


def extend_df(df, reduced_vectors, labels):
    df['x'] = reduced_vectors[:, 0]
    df['y'] = reduced_vectors[:, 1]
    df['z'] = reduced_vectors[:, 2]
    df['cluster'] = labels


if __name__ == "__main__":
    all_files = get_all_files()
    for path in tqdm(all_files):
        print(path)
        result = pipeline(f'{mypath_input}/{path}', embedding_model='sentence transformer', alg='PCA',
                          cut_outliers=False,
                          show_plot=False, plot_name=f'{path[:-4]}')
        if not result:
            continue

        reduced_vectors, labels, df, model = result

        extend_df(df, reduced_vectors, labels)

        df.to_csv(f'{mypath_output}/results_processed/{path[:-4]}_processed.csv', index=False)

        with open(f'{mypath_output}/models/{path[:-4]}_processed.pickle', 'wb') as file:
            pickle.dump(model, file)
