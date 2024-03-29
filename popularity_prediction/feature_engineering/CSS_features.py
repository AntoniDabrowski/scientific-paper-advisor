import pandas as pd
import numpy as np
from collections import defaultdict as dd
from tqdm.auto import tqdm
import pickle
import matplotlib.pyplot as plt
from matplotlib import cm
from sentence_transformers import SentenceTransformer
import json


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
        bins[int(bin_count * (value / max_value)) + 1].append(key)
    return bins


def calculate_inverse_bins(bins):
    inverse_bins = {}
    for bin_number, values in bins.items():
        for n_gram in values:
            inverse_bins[n_gram] = bin_number
    return inverse_bins


def evaluate_bins(df, inverse_bins, n=2, plot_title=""):
    bins_evaluation = {i: 1 for i in range(1, 11)}
    l1 = df['title'].tolist()
    l2 = df['abstract'].tolist()
    for i in tqdm(range(len(l1))):
        title, abstract = l1[i], l2[i]
        text = f"{title} {abstract}"
        if len(text) <= n:
            continue
        current = text[:n]
        for character in text[n:]:
            bins_evaluation[inverse_bins.get(current, 1)] += 1
            current = current[1:] + character
    for k in bins_evaluation.keys():
        bins_evaluation[k] = np.log(bins_evaluation[k])

    Xs = [i for i in range(1, len(bins_evaluation.keys()))]
    Ys = [bins_evaluation[k] for k in Xs]
    colors = cm.jet(1 - (np.array(Xs) / float(max(Xs))))

    plt.bar(Xs, Ys, color=colors)
    plt.title(plot_title)
    plt.xlabel('bin')
    plt.ylabel(f'Log count of {n}-grams')
    plt.show()


def CSS_vector(text, inverse_bins, n):
    bins_evaluation = dd(int)
    if len(text) <= n:
        return [0.0] * n
    current = text[:n]
    for character in text[n:]:
        bins_evaluation[inverse_bins.get(current, 1)] += 1
        current = current[1:] + character
    return [np.log(bins_evaluation[i]) for i in range(1, n + 1)]


import unicodedata as ud


def is_latin(uchr, latin_letters):
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))


def only_roman_chars(unistr):
    latin_letters = {}
    return all(is_latin(uchr, latin_letters)
               for uchr in unistr
               if uchr.isalpha())


def category_comparison(n=2, categories=['cs.AI', 'physics.app']):
    df = pd.read_csv('../data/edition_2/semanticscholar_results2_quantiles_categories.csv')

    category_mapping = json.load(open('../../extension/scripts/categories.json'))
    inverse_bins = pickle.load(open(f'../submodules/inverse_bins_{n}_gram.pickle', 'rb'))

    # for domain in category_mapping.keys():
    for domain in categories:
        df_temp = df[df["domain"] == domain].copy()
        if df_temp.shape[0] > 0:
            evaluate_bins(df_temp, inverse_bins, n=n, plot_title=category_mapping[domain])


def compute_categories():
    KNN_model = pickle.load(open('../../backend/frquestions/category_analysis/model.pickle', 'rb'))
    SentenceTransformer_loaded = SentenceTransformer('all-MiniLM-L6-v2')

    def parse_row(row):
        if row["title"] and row["abstract"]:
            return f'{row["title"]}\n{row["abstract"]}'
        return "economy, economy, this has to be categorised as the economy"

    df = pd.read_csv(open('../data/edition_2/semanticscholar_results2_quantiles.csv', encoding='UTF-8'))
    texts = [parse_row(row) for _, row in tqdm(df.iterrows())]
    embeddings = SentenceTransformer_loaded.encode(texts)
    categories = KNN_model.predict(embeddings)
    df["domain"] = categories
    df.to_csv('../data/edition_2/semanticscholar_results2_quantiles_categories.csv')


def CSS_single_paper(n=2):
    df = pd.read_csv('../data/edition_2/semanticscholar_results2_quantiles_categories.csv')

    # category_mapping = json.load(open('../../extension/scripts/categories.json'))
    inverse_bins = pickle.load(open(f'../submodules/inverse_bins_{n}_gram.pickle', 'rb'))
    max_count = np.max(df['citationcount'])
    df_temp = df[df['citationcount'] == max_count]
    evaluate_bins(df_temp, inverse_bins, n=n,
                  plot_title=f"\"{next(df_temp.iterrows())[1]['title']}\" ({max_count} citations)")
    for i in range(100):
        df_temp = df[df['citationcount'] == 7].iloc[[i]]
        evaluate_bins(df_temp, inverse_bins, n=n,
                      plot_title=f"\"{next(df_temp.iterrows())[1]['title']}\" (7 citations)")


if __name__ == '__main__':
    CSS_single_paper()

    # n = 3
    # df = pd.read_csv(open('../data/edition_2/semanticscholar_results2_quantiles.csv', encoding='UTF-8'))
    # n_occurences = n_gram_frequencies(df,n=n)
    #
    # bins = calculate_bins(n_occurences, bin_count=10)
    # print(bins[10][:50])
    #
    # inverse_bins = calculate_inverse_bins(bins)
    # pickle.dump(inverse_bins, open(f'../submodules/inverse_bins_{n}_gram.pickle', 'wb'))
    # evaluate_bins(df, inverse_bins, n=n, plot_title = f'Characters {n}-grams CSS')
