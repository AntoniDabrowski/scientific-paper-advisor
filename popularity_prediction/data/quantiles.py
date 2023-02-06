import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)


def hist_citation_count(df=None):
    if type(df) != pd.core.frame.DataFrame:
        df = pd.read_csv(open('semanticscholar_results.csv', encoding='UTF-8'))
    plt.hist(df['citationcount'].tolist())
    plt.xscale('log')
    plt.yscale('log')
    plt.title("Citation count")
    plt.ylabel("Number of papers")
    plt.xlabel("Number of citations")
    plt.show()


def compute_quantiles(df=None):
    if type(df) != pd.core.frame.DataFrame:
        df = pd.read_csv(open('semanticscholar_results.csv', encoding='UTF-8'))
    citations = df["citationcount"].tolist()
    # l = np.linspace(0, 0.95, 1000)
    l = [0.25, 0.5, 0.75]
    quantiles = np.quantile(citations, l)
    print(quantiles.astype(int))
    # plt.scatter(l, quantiles)
    # # plt.yscale('log')
    # plt.show()


def trim_data_for_quantiles(df):
    def drop_percent(to_drop_df, percent):
        remove_n = int((to_drop_df.shape[0] * percent))
        drop_indices = np.random.choice(to_drop_df.index, remove_n, replace=False)
        to_drop_df.drop(drop_indices, inplace=True)

    citation_count = {val: df[df['citationcount'] == val].copy() for val in df['citationcount'].unique()}

    # remove_n = int((citation_count[0].shape[0] / df.shape[0] - 0.147) * df.shape[0])
    # drop_indices = np.random.choice(citation_count[0].index, remove_n, replace=False)
    # citation_count[0].drop(drop_indices, inplace=True)

    for i in range(8, 16):
        drop_percent(citation_count[i], 0.3)

    return pd.concat(list(citation_count.values()))


def map_class(x):
    if x == 0:
        return 0
    elif x < 5:
        return 1
    elif x < 16:
        return 2
    return 3