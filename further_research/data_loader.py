import pandas as pd
from collections import defaultdict as dd
import matplotlib.pyplot as plt


def load_data(path):
    df = pd.read_csv(path)
    df = df.fillna("")
    df.reset_index()
    records = dd(str)

    for index, record in df.iterrows():
        records[index] += record['further research line'] + ' ' if type(record['further research line']) == str else ""
        records[index] += record['further research prefix'] + ' ' if type(
            record['further research prefix']) == str else ""
        records[index] += record['further research suffix'] + ' ' if type(
            record['further research suffix']) == str else ""
        if not records[index]:
            del records[index]

    return df, records


def prepare_chunks(df):
    records = []

    for _, record in df.iterrows():
        row = ""
        row += record['further research prefix'] + ' ' if type(record['further research prefix']) == str else ""
        row += record['further research line'] + ' ' if type(record['further research line']) == str else ""
        row += record['further research suffix'] + ' ' if type(record['further research suffix']) == str else ""
        if row:
            records.append(row)
        else:
            records.append(None)
    df['further research'] = records
    categories = df['primary category'].unique().tolist()

    fr = df[['url', 'title', 'further research', 'primary category']]
    fr = fr.dropna()
    chunks_fr = {category: fr[fr['primary category'] == category] for
                 category in categories}

    ab = df[['url', 'title', 'abstract', 'primary category']]
    ab = ab.dropna()
    chunks_ab = {category: ab[ab['primary category'] == category] for
                 category in categories}

    return chunks_fr, chunks_ab


if __name__ == "__main__":
    df = pd.read_csv('../utils/FRDownloader/all_results/extended_search_list.csv')