import unicodedata as ud
import pandas as pd
import numpy as np
import json


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


def remove_too_empty_columns(df):
    df.drop(columns=['publicationdate','publicationvenueid','publicationtypes'], inplace=True)


def remove_nans(df):
    df.drop(df[df['citationcount'].isna()].index, inplace=True)
    df.drop(df[df['abstract'].isna()].index, inplace=True)
    df.drop(df[df['citationcount'].isna()].index, inplace=True)
    df.drop(df[df['citationcount'].str.isnumeric().isna()].index, inplace=True)
    df.drop(df[~df['citationcount'].str.isnumeric()].index, inplace=True)


def fill_nans(df):
    values = {"venue":"", "journal":"{}"}
    df.fillna(value=values, inplace=True)

def preprocessing(df):
    remove_nans(df)
    remove_not_latin(df)
    remove_too_empty_columns(df)
    fill_nans(df)


if __name__ == '__main__':
    # title,abstract,authors,venue,publicationvenueid,isopenaccess,publicationtypes,publicationdate,year,citationcount,journal
    df = pd.read_csv(open('../data/edition_2/semanticscholar_results2.csv', encoding='UTF-8'))
    preprocessing(df)
    df.to_csv('../data/edition_2/semanticscholar_results2_preprocessed.csv')
