import pandas as pd
import numpy as np
from collections import defaultdict as dd
from tqdm.auto import tqdm
import pickle
import matplotlib.pyplot as plt
from matplotlib import cm


def n_gram_frequencies(df, n=2):
    n_occurences = dd(int)
    total = 0
    l1 = df['title'].tolist()
    l2 = df['abstract'].tolist()
    for i in tqdm(range(len(l1))):
        title, abstract = l1[i], l2[i]
        text = f"{title} {abstract}"
        if len(text) <= n:
            continue
        current = text[:n]
        for character in text[n:]:
            n_occurences[current] += 1
            total += 1
            current = current[1:] + character

    for key in n_occurences.keys():
        n_occurences[key] = np.log(n_occurences[key])

    return n_occurences

def calculate_bins(n_occurences, bin_count=10):
    max_value = max(n_occurences.values()) + 0.001
    bins = dd(list)

    for key, value in n_occurences.items():
        bins[int(bin_count * (value/max_value)) + 1].append(key)
    return bins

def calculate_inverse_bins(bins):
    inverse_bins = {}
    for bin_number, values in bins.items():
        for n_gram in values:
            inverse_bins[n_gram] = bin_number
    return inverse_bins

def evaluate_bins(df, inverse_bins, n=2):
    bins_evaluation = dd(int)
    l1 = df['title'].tolist()
    l2 = df['abstract'].tolist()
    for i in tqdm(range(len(l1))):
        title, abstract = l1[i], l2[i]
        text = f"{title} {abstract}"
        if len(text) <= n:
            continue
        current = text[:n]
        for character in text[n:]:
            bins_evaluation[inverse_bins.get(current,1)] += 1
            current = current[1:] + character
    for k in bins_evaluation.keys():
        bins_evaluation[k] = np.log(bins_evaluation[k])

    Xs = [i for i in range(1,len(bins_evaluation.keys()))]
    Ys = [bins_evaluation[k] for k in Xs]
    colors = cm.jet(1-(np.array(Xs) / float(max(Xs))))

    plt.bar(Xs,Ys, color=colors)
    plt.title(f'Characters {n}-grams CSS')
    plt.xlabel('bin')
    plt.ylabel(f'Log count of {n}-grams')
    plt.show()

def CSS_vector(text, inverse_bins, n):
    bins_evaluation = dd(int)
    if len(text) <= n:
        return [0.0] * n
    current = text[:n]
    for character in text[n:]:
        bins_evaluation[inverse_bins.get(current,1)] += 1
        current = current[1:] + character
    return [np.log(bins_evaluation[i]) for i in range(1,n+1)]


if __name__=='__main__':
    n = 3
    # df = pd.read_csv(open('semanticscholar_results_preprocessed.csv', encoding='UTF-8'))
    # n_occurences = n_gram_frequencies(df,n=n)
    # pickle.dump(n_occurences, open(f'n_gram_occurences_{n}_gram.pickle', 'wb'))

    n_occurences = pickle.load(open('n_gram_occurences_2_gram.pickle', 'rb'))
    bins = calculate_bins(n_occurences, bin_count=10)
    print(bins[1][:100])

    # inverse_bins = calculate_inverse_bins(bins)
    # pickle.dump(inverse_bins, open(f'inverse_bins_{n}_gram.pickle', 'wb'))

    # evaluate_bins(df, inverse_bins, n=n)
