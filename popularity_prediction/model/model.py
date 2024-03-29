import pandas as pd
import numpy as np
from numpy import genfromtxt
import pickle
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPClassifier

from popularity_prediction.data.quantiles import map_class


def train_model_LinearRegression(X, Y, save=True):
    # 25.01%
    model = LinearRegression().fit(X, Y)
    if save:
        pickle.dump(model, open('pretrained_models/pp_LinearRegression.pickle', 'wb'))
    return model


def train_model_RidgeRegression(X, Y, save=True):
    # 25.01%
    model = Ridge().fit(X, Y)
    if save:
        pickle.dump(model, open('pretrained_models/pp_RidgeRegression.pickle', 'wb'))
    return model


def train_model_MLPClassifier(X, Y, layers, max_iter=100, save=True, verbose=True, output_name=""):
    layers = [X.shape[1]] + layers
    model = MLPClassifier(random_state=1, max_iter=max_iter, hidden_layer_sizes=layers, verbose=verbose)
    model.fit(X, Y)
    if save:
        pickle.dump(model, open(f'pretrained_models/pp_MLPClassifier_{output_name}.pickle', 'wb'))
    return model


def accuracy(model, X, Y):
    Y_pred = model.predict(X)
    Y_pred_int = np.array(Y_pred).astype(int)
    Y = np.array(Y).astype(int)
    # n = 10
    # for y, y_ in zip(Y[:n], Y_pred_int[:n]):
    #     print(y, y_)
    return np.sum(np.equal(Y, Y_pred_int)) / Y.shape[0]


def load_data_semantic_embedding(proportion=0.7):
    df = pd.read_csv(open('semanticscholar_results_to_quantiles.csv', encoding='UTF-8'))
    dense_embeddings = genfromtxt('dense_embeddings.csv', delimiter=',')
    categories = np.array([df['category'].tolist()]).reshape(-1, 1)
    total = dense_embeddings.shape[0]

    joined = np.hstack([categories, dense_embeddings])
    np.random.shuffle(joined)

    x_train, x_test = joined[:int(total * proportion), 1:], joined[int(total * proportion):, 1:]
    y_train, y_test = joined[:int(total * proportion), 0], joined[int(total * proportion):, 0]
    return x_train, x_test, y_train, y_test


def load_data_lexical_embeddings(proportion=0.75):
    df = pd.read_csv(open('semanticscholar_results_embeddings.csv', encoding='UTF-8'))
    categories = np.array([df['category'].tolist()]).reshape(-1, 1)
    to_drop = [name for name in df.columns if name[0].isnumeric()]
    df.drop(columns=['category'] + to_drop, inplace=True)
    embeddings = df.to_numpy()
    total = df.shape[0]

    joined = np.hstack([categories, embeddings])
    np.random.shuffle(joined)

    x_train, x_test = joined[:int(total * proportion), 1:], joined[int(total * proportion):, 1:]
    y_train, y_test = joined[:int(total * proportion), 0], joined[int(total * proportion):, 0]
    return x_train, x_test, y_train, y_test


def load_data(proportion=0.75, lexical=True, semantic=True, side_info=True):
    df = pd.read_csv(open('../data/edition_2/semanticscholar_results2_embeddings.csv', encoding='UTF-8'))
    to_drop_names = ["" if lexical else "lex", "" if semantic else "sem", "" if side_info else "side"]
    to_drop = [column for column in df.columns if column.split('_')[0] in to_drop_names]
    categories = np.array([df['category'].tolist()]).reshape(-1, 1)
    df.drop(columns=['category'] + to_drop, inplace=True)
    embeddings = df.to_numpy()
    total = df.shape[0]

    joined = np.hstack([categories, embeddings])
    np.random.shuffle(joined)

    x_train, x_test = joined[:int(total * proportion), 1:], joined[int(total * proportion):, 1:]
    y_train, y_test = joined[:int(total * proportion), 0], joined[int(total * proportion):, 0]
    return x_train, x_test, y_train, y_test


if __name__ == '__main__':
    print('Loading data')
    datasets = [[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [0, 1, 1],
                [1, 0, 1],
                [1, 1, 0],
                [1, 1, 1]]

    for lexical, semantic, side_info in datasets:
        x_train, x_test, y_train, y_test = load_data(lexical=lexical, semantic=semantic, side_info=side_info)

        # model = train_model_LinearRegression(x_train, y_train)
        # model = train_model_RidgeRegression(x_train, y_train)
        layers = [[70, 40, 20],
                  [40, 40, 40, 40],
                  [40, 40, 40, 40, 40],
                  [100, 80, 60, 40, 20],
                  [200, 160, 120, 80, 40],
                  [300, 150, 100, 50, 25],
                  [250, 250, 125],
                  [80, 120, 140, 160, 140, 120, 80],
                  [20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                  [500, 400, 300, 150, 50],
                  [700, 700, 700],
                  [900, 500, 200, 100, 50],
                  [1000, 800, 700, 600, 500, 400, 300, 200, 100, 50, 20],
                  [300, 300, 300]]

        for layer in layers:
            try:
                max_iter = 2000
                datasets_notation = f'{lexical}{semantic}{side_info}'
                model = train_model_MLPClassifier(x_train, y_train, layer, max_iter, verbose=True, save=False,
                                                  output_name=datasets_notation)
                test_acc = str(accuracy(model, x_test, y_test))[:7]
                train_acc = str(accuracy(model, x_train, y_train))[:7]
                print(f"DATA: {datasets_notation}, TRAIN ACC: {train_acc}, TEST ACC: {test_acc}, LAYER: {layer}")
            except:
                print(layer, 'ERROR')
