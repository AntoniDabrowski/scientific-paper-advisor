import pandas as pd
import nltk


def verify_primary_topic():
    pass


def prepare_nltk():
    try:
        nltk.data.find('punkt')
    except LookupError:
        nltk.download('punkt')


def default_fr_dataframe():
    return pd.DataFrame(columns={
        'further research': pd.Series('str'),
        'publication date': pd.Series('date'),
        'tags': pd.Series('str'),
        'title': pd.Series('str'),
        'authors': pd.Series('str'),
        'abstract': pd.Series('str')
    })
