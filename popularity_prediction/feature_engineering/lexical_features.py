import numpy as np
import pandas as pd
import string
from nltk import pos_tag, word_tokenize, sent_tokenize
from collections import defaultdict as dd
import pickle

inverse_bins_2_grams = pickle.load(open(f'../submodules/inverse_bins_2_gram.pickle', 'rb'))
inverse_bins_3_grams = pickle.load(open(f'../submodules/inverse_bins_3_gram.pickle', 'rb'))


def add_tag(arr):
    return [f'lex_{name}' for name in arr]


def character_level(text):
    total = len(text) + 1
    alphabetic = np.sum(list(map(lambda character: character.isalpha(), text)))
    numeric = np.sum(list(map(lambda character: character.isdigit(), text)))
    punctuation = np.sum(list(map(lambda character: character in string.punctuation, text)))
    space = np.sum(list(map(lambda character: character.isspace(), text)))
    lower = np.sum(list(map(lambda character: character.islower() if character.isalpha() else False, text)))
    upper = np.sum(list(map(lambda character: character.isupper() if character.isalpha() else False, text)))
    values = [alphabetic / total,
              numeric / total,
              punctuation / total,
              space / total,
              lower / (alphabetic + 1),
              upper / (alphabetic + 1)]
    labels = ['alphabetic',
              'numeric',
              'punctuation',
              'space',
              'lower',
              'upper']
    return values, add_tag(labels)


def sentence_level(text):
    sentences = sent_tokenize(text)
    if len(sentences) > 0:
        avg_tokens = np.mean([len(word_tokenize(sentence)) for sentence in sentences])
    else:
        avg_tokens = 0
    return [len(sentences), avg_tokens], add_tag(['num_sentences', 'avg_tokens'])


def POS_frequency(text):
    tags = "CC CD DT EX FW IN JJ JJR JJS LS MD NN NNP NNPS NNS PDT POS PRP PRP$ RB RBR RBS RP SYM TO UH VB VBD VBG VBN VBP VBZ WDT WP WP$ WRB"
    tags_occurrences = dd(int)
    total = 1
    for _, tag in pos_tag(word_tokenize(text)):
        tags_occurrences[tag] += 1
        total += 1
    return [tags_occurrences[tag] / total for tag in tags.split()], add_tag(tags.split())


def POS_bigrams_frequency(text):
    popular_bigram_tags = ['NNP-NNS', 'VBD-JJ', 'VBD-RB', 'NNS-VBD', 'JJ-NNP', 'CD-JJ', 'CC-CD', 'VBD-DT', 'CD-NN',
                           'JJ-CD', 'VBP-IN', 'JJ-PNC', 'NN-NNP', 'VBD-IN', 'RB-VBN', 'JJ-JJ', 'VBD-VBN', 'PRP-VBD',
                           'NN-CD', 'NNP-VBD', 'NNS-PNC', 'IN-CD', 'NN-VBD', 'NNS-VBN', 'NNP-CC']
    tags_occurrences = dd(int)
    total = 1
    text_tags = [tag for _, tag in pos_tag(word_tokenize(text))]

    for i in range(1, len(text_tags)):
        bigram_tags = f'{text_tags[i - 1]}-{text_tags[i]}'
        if bigram_tags in popular_bigram_tags:
            tags_occurrences[bigram_tags] += 1
            total += 1
    return [tags_occurrences[tag] / total for tag in popular_bigram_tags], add_tag(popular_bigram_tags)


def CSS_vector(text, n=2, bins_count=10):
    assert n in [2, 3]
    if n == 2:
        inverse_bins = inverse_bins_2_grams
    else:
        inverse_bins = inverse_bins_3_grams

    bins_evaluation = dd(lambda: 1)
    if len(text) <= n:
        return [0.0] * bins_count, add_tag([f'bin{i}' for i in range(1, bins_count + 1)])
    current = text[:n]
    for character in text[n:]:
        bins_evaluation[inverse_bins.get(current, 1)] += 1
        current = current[1:] + character
    return [np.log(bins_evaluation[i]) for i in range(1, bins_count + 1)], \
           add_tag([f'bin{i}' for i in range(1, bins_count + 1)])

# text = """Cashless India is a mission launched by the Government of to reduce dependency of Indian economy on cash and to bring hoards of stashed black money lying unused into the banking system. The country embarked upon this transition to a cashless economy when the government took the revolutionary step of demonetisation of old currency notes of Rs 500 and Rs 1000 on November 08, 2016. The Union government’s demonetization initiative and the subsequent drive towards developing a cashless India have invited its share of both bricks and bouquets. The latest World Bank report has mentioned that the demonetisation will not have any long-term adverse effect on the Indian economy. But it will prove beneficial with growth of the Indian economy rising to 7.6% in fiscal year 2018. In India Liquidity expansion in the banking system post-demonetisation has helped the banks to lower lending rates, which in turn is bound to lift economic activity. This paper deals with the role of cashless economy in economic development and also reflects the positive and negative impact on the economy."""
# n = 2
# print(CSS_vector(text,n))
