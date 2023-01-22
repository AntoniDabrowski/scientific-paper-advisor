import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from load_data import data_loader, split_data
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
from collections import defaultdict as dd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

SentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')


def get_embeddings(df):
    texts = df[["title", "abstract"]].apply(".\n".join, axis=1).tolist()
    return SentenceTransformerModel.encode(texts)


def KNN_train(texts_embeddings, labels, k=3):
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(texts_embeddings, labels)
    return model


def predict(texts_embeddings, labels, model):
    prediction = model.predict(texts_embeddings)
    return accuracy_score(labels, prediction)


def test_over_k(train, validate):
    embedding_train = get_embeddings(train)
    embedding_validate = get_embeddings(validate)

    z = 1.96
    n = embedding_validate.shape[1]
    k = range(1, 21)
    scores = []
    upper_confidence_interval = []
    lower_confidence_interval = []
    for _k in tqdm(k):
        model = KNN_train(embedding_train, train["primary category"], _k)
        P = predict(embedding_validate, validate["primary category"], model)
        scores.append(P)

        confidence_interval = z * np.sqrt(P * (1 - P) / n)
        upper_confidence_interval.append(min(1 - P, confidence_interval))
        lower_confidence_interval.append(min(P, confidence_interval))

    plt.errorbar(k, scores, yerr=np.array([lower_confidence_interval, upper_confidence_interval]), fmt='o', color='k')
    plt.title('KNN classifier with 95% confidence interval')
    plt.xlabel('K')
    plt.ylabel('Accuracy')
    plt.xticks(k, list(map(str, k)))
    plt.show()


def test_over_categories(train, validate, k):
    embedding_train = get_embeddings(train)
    embedding_validate = get_embeddings(validate)

    model = KNN_train(embedding_train, train["primary category"], k)
    predictions = model.predict(embedding_validate)
    positive = dd(int)
    negative = dd(int)
    for true_value, predicted_value in zip(validate["primary category"], predictions):
        if true_value == predicted_value:
            positive[true_value] += 1
        else:
            negative[true_value] += 1

    avg = []
    upper_confidence_interval = []
    lower_confidence_interval = []
    labels = []
    z = 1.96
    for label in positive.keys():
        n = positive[label] + negative[label]
        P = positive[label] / n

        labels.append(label)
        avg.append(P)
        confidence_interval = z * np.sqrt(P * (1 - P) / n)
        upper_confidence_interval.append(min(1 - P, confidence_interval))
        lower_confidence_interval.append(min(P, confidence_interval))

    plt.figure()
    plt.errorbar(labels, avg, yerr=np.array([lower_confidence_interval, upper_confidence_interval]), fmt='o', color='k')
    plt.axhline(accuracy_score(validate["primary category"], predictions), ls='--')
    plt.title(f'KNN classifier k={k} with 95% confidence interval')
    plt.xlabel('Categories')
    plt.ylabel('Accuracy')
    plt.tick_params(
        axis='x',
        which='both',
        bottom=False,
        top=False,
        labelbottom=False)
    mean_patch = mlines.Line2D([], [], color='#1f77b4', markersize=15, label='Avg accuracy', linestyle='--')
    plt.legend(handles=[mean_patch])
    plt.show()


if __name__ == "__main__":
    df = data_loader('../../utils/FRDownloader/results/mass_parsing.csv')
    train, validate, _ = split_data(df)

    test_over_k(train, validate)
    test_over_categories(train, validate, k=1)
