import pandas as pd
import numpy as np
from numpy import genfromtxt
import pickle
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPClassifier
from quantiles import map_class
np.random.seed(0)

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

def train_model_MLPClassifier(X, Y, save=True):
    # only dense embeddings
    # 30.94%
    # 31.03%
    # 31.36%
    # semantic + lexical embeddings
    # 25.42%
    # lexical embeddings
    # 25.42%
    model = MLPClassifier(random_state=1, max_iter=1500, hidden_layer_sizes=(X.shape[1],200,4),verbose=True)
    model.fit(X, Y)
    if save:
        pickle.dump(model, open('pretrained_models/pp_MLPClassifier_4.pickle', 'wb'))
    return model

def accuracy(model, X, Y):
    Y_pred = model.predict(X)
    Y_pred_int = np.array(list(map(lambda x: map_class(x), Y_pred))).astype(int)
    Y = np.array(Y).astype(int)
    for y, y_ in zip(Y[:10],Y_pred_int[:10]):
        print(y, y_)
    return np.sum(np.equal(Y,Y_pred_int)) / Y.shape[0]


def load_data_semantic_embedding(proportion=0.7):
    df = pd.read_csv(open('semanticscholar_results_to_quantiles.csv', encoding='UTF-8'))
    dense_embeddings = genfromtxt('dense_embeddings.csv', delimiter=',')
    categories = np.array([df['category'].tolist()]).reshape(-1,1)
    total = dense_embeddings.shape[0]

    joined = np.hstack([categories,dense_embeddings])
    np.random.shuffle(joined)

    x_train, x_test = joined[:int(total * proportion),1:], joined[int(total * proportion):,1:]
    y_train, y_test = joined[:int(total * proportion),0], joined[int(total * proportion):,0]
    return x_train, x_test, y_train, y_test

def load_data_lexical_embeddings(proportion=0.75):
    df = pd.read_csv(open('semanticscholar_results_embeddings.csv', encoding='UTF-8'))
    categories = np.array([df['category'].tolist()]).reshape(-1,1)
    to_drop = [name for name in df.columns if name[0].isnumeric()]
    df.drop(columns = ['category']+to_drop,inplace=True)
    embeddings = df.to_numpy()
    total = df.shape[0]

    joined = np.hstack([categories,embeddings])
    np.random.shuffle(joined)

    x_train, x_test = joined[:int(total * proportion),1:], joined[int(total * proportion):,1:]
    y_train, y_test = joined[:int(total * proportion),0], joined[int(total * proportion):,0]
    return x_train, x_test, y_train, y_test

def load_data(proportion=0.75):
    df = pd.read_csv(open('semanticscholar_results_embeddings.csv', encoding='UTF-8'))
    categories = np.array([df['category'].tolist()]).reshape(-1,1)
    df.drop(columns = ['category'],inplace=True)
    embeddings = df.to_numpy()
    total = df.shape[0]

    joined = np.hstack([categories,embeddings])
    np.random.shuffle(joined)

    x_train, x_test = joined[:int(total * proportion),1:], joined[int(total * proportion):,1:]
    y_train, y_test = joined[:int(total * proportion),0], joined[int(total * proportion):,0]
    return x_train, x_test, y_train, y_test

if __name__ == '__main__':
    # x_train, x_test, y_train, y_test = load_data()
    x_train, x_test, y_train, y_test = load_data_lexical_embeddings()
    # model = pickle.load(open('pretrained_models/pp_RidgeRegression.pickle', 'rb'))

    model = train_model_MLPClassifier(x_train, y_train)
    print(accuracy(model, x_test, y_test))
