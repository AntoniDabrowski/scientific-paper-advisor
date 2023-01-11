import pandas as pd


def load_data(path):
    df = pd.read_csv(path)
    df = df.fillna("")
    df.reset_index()
    records = dict()

    for index, record in df.iterrows():
        records[index] = ""
        # records[index] += record['further research line'] + ' ' if type(record['further research line']) == str else ""
        records[index] += record['further research prefix'] + ' ' if type(
            record['further research prefix']) == str else ""
        # records[index] += record['further research suffix'] + ' ' if type(record['further research suffix']) == str else ""
        if not records[index]:
            del records[index]

    return df, records


if __name__ == "__main__":
    df = load_data('./data/training_data.cs.AI.csv')
    for txt in df['abstract'][:10]:
        print(txt)
