import numpy as np
import pandas as pd
import string
from nltk import pos_tag, word_tokenize, sent_tokenize
from collections import defaultdict as dd
import pickle

top_authors = pickle.load(open('../submodules/top_authors.pickle', 'rb'))
top_affiliations = pickle.load(open('../submodules/top_affiliations.pickle', 'rb'))
top_journals = pickle.load(open('../submodules/top_journals.pickle', 'rb'))
top_venues = pickle.load(open('../submodules/top_venues.pickle', 'rb'))


def add_tag(arr):
    return [f'side_{name}' for name in arr]


def authors_value(authors):
    in_top_authors = False
    in_top_affiliations = False
    for author in eval(authors):
        if author['name'] in top_authors:
            in_top_authors = True
        if 'affiliation' in author and author['affiliation'] and author['affiliation'] in top_affiliations:
            in_top_affiliations = True
    return [float(in_top_authors), float(in_top_affiliations)], add_tag(["top_author", "top_affiliation"])


def venue_value(venue):
    if venue:
        return [float(venue in top_venues)], add_tag(['top_venue'])
    else:
        return [0.5], add_tag(['top_venue'])

def is_open_access_value(is_open_access):
    if is_open_access:
        return [float(is_open_access)], add_tag(['open_access'])
    else:
        return [0.5], add_tag(['open_access'])


def journal_value(journal):
    if journal:
        return [float(journal in top_journals)], add_tag(['top_journal'])
    else:
        return [0.5], add_tag(['top_journal'])


if __name__ == '__main__':
    df = pd.read_csv(open('../data/edition_2/semanticscholar_results2_quantiles.csv', encoding='UTF-8'))
