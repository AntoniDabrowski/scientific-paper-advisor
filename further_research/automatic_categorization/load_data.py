import pandas as pd
import numpy as np


def data_loader(path):
    df = pd.read_csv(path)
    return df[["primary category", "title", "abstract"]]


def split_data(df):
    return np.split(df.sample(frac=1, random_state=42),
                    [int(.6 * len(df)), int(.8 * len(df))])


if __name__ == "__main__":
    df = data_loader('../../utils/FRDownloader/results/mass_parsing.csv')
    train, validate, test = split_data(df)
