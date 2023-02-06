import unicodedata as ud
import pandas as pd
import numpy as np


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


def remove_not_latin(df):
    # removing 9216 non-latin papers
    mask = df['abstract'].apply(lambda x: not only_roman_chars(str(x)))
    df.drop(df[mask].index, inplace=True)
    return df


def remove_publication_date(df):
    df.drop(columns=['publicationdate'], inplace=True)


def remove_nans(df):
    df.drop(df[df['citationcount'].isna()].index, inplace=True)
    df.drop(df[df['abstract'].isna()].index, inplace=True)


def fill_nans(df):
    values = {"year": 2017, "authors": ""}
    df.fillna(value=values, inplace=True)

def preprocessing(df):
    fill_nans(df)
    remove_nans(df)
    remove_not_latin(df)
    remove_publication_date(df)


if __name__ == '__main__':
    df = pd.read_csv(open('semanticscholar_results.csv', encoding='UTF-8'))
    preprocessing(df)
    df.to_csv('semanticscholar_results_preprocessed.csv')
