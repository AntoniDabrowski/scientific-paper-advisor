import nltk
import pandas as pd


def verify_primary_topic():
    pass


def prepare_nltk():
    try:
        nltk.data.find('punkt')
    except LookupError:
        nltk.download('punkt')


def default_fr_dataframe():
    return pd.DataFrame(columns={
        'further research line': pd.Series('str'),
        'further research prefix': pd.Series('str'),
        'further research suffix': pd.Series('str'),
        'publication date': pd.Series('date'),
        'title': pd.Series('str'),
        'primary category': pd.Series('str'),
        'categories': pd.Series('str'),
        'authors': pd.Series('str'),
        'abstract': pd.Series('str')
    })


def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default
