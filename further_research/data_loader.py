import pandas as pd
from collections import defaultdict as dd


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
    df = df[['url', 'title', 'further research', 'abstract', 'primary category']]

    return {category:df[df['primary category'] == category] for category in df['primary category'].unique().tolist()}


if __name__ == "__main__":
    df = pd.read_csv('../utils/FRDownloader/all_results/extended_search_list.csv')
    chunks = prepare_chunks(df)
    print(chunks.keys())

    # print(repr(df['primary category'].value_counts().tolist()))
    # df.head(10).to_csv('./out.csv', index=False)
