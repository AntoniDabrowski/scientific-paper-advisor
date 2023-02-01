import numpy as np
import pandas as pd
import string
from nltk import pos_tag, word_tokenize, sent_tokenize
import pickle
import json
from collections import defaultdict as dd
from tqdm.auto import tqdm
import matplotlib.pyplot as plt


def authors_ranking(authors, citation_count):
    ranking_authors = dd(list)
    ranking_affiliations = dd(list)
    for authors, citations in tqdm(zip(authors.tolist(), citation_count.tolist())):
        try:
            authors = eval(authors)
        except:
            print(authors)
        for author in authors:
            if 'name' in author:
                ranking_authors[author['name']].append(citations)
            if 'affiliations' and author['affiliations']:
                for aff in author['affiliations']:
                    ranking_affiliations[aff].append(citations)

    ranking_authors_mean = {author: np.mean(citations) for author, citations in ranking_authors.items()}
    ranking_affiliations_mean = {affiliation: np.mean(citations) for affiliation, citations in
                                 ranking_affiliations.items()}

    authors = sorted(ranking_authors_mean.items(), key=lambda x: x[1], reverse=True)[:2000]
    affiliations = sorted(ranking_affiliations_mean.items(), key=lambda x: x[1], reverse=True)[:300]
    pickle.dump([author for author, _ in authors], open('../submodules/top_authors.pickle', 'wb'))
    pickle.dump([affiliation for affiliation, _ in affiliations], open('../submodules/top_affiliations.pickle', 'wb'))


def venue_value(venues, citation_count):
    ranking_venues = dd(list)
    for venue, citations in tqdm(zip(venues.tolist(), citation_count.tolist())):
        ranking_venues[venue].append(citations)

    ranking_venues_mean = {venue: np.mean(citations) for venue, citations in ranking_venues.items()}

    venues = sorted(ranking_venues_mean.items(), key=lambda x: x[1], reverse=True)
    pickle.dump([venue for venue, _ in venues][:200], open('../submodules/top_venues.pickle', 'wb'))


def journal_value(journals, citation_count):
    ranking_journals = dd(list)
    for journal, citations in tqdm(zip(journals.tolist(), citation_count.tolist())):
        journal = eval(journal).get('name')
        if journal:
            ranking_journals[journal].append(citations)

    ranking_journals_mean = {journal: np.mean(citations) for journal, citations in ranking_journals.items()}

    journals = sorted(ranking_journals_mean.items(), key=lambda x: x[1], reverse=True)
    pickle.dump([journal for journal, _ in journals][:200], open('../submodules/top_journals.pickle', 'wb'))


if __name__ == '__main__':
    df = pd.read_csv(open('../data/edition_2/semanticscholar_results2_quantiles.csv', encoding='UTF-8'))

    # plt.hist(auth_ranking.values())
    # plt.yscale('log')
    # plt.show()
