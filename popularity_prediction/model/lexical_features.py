import numpy as np
import pandas as pd
import string
from nltk import pos_tag, word_tokenize, sent_tokenize
from collections import defaultdict as dd


def character_level(text):
    total = len(text) + 1
    alphabetic = np.sum(list(map(lambda character: character.isalpha(), text)))
    numeric = np.sum(list(map(lambda character: character.isdigit(), text)))
    punctuation = np.sum(list(map(lambda character: character in string.punctuation, text)))
    space = np.sum(list(map(lambda character: character.isspace(), text)))
    lower = np.sum(list(map(lambda character: character.islower() if character.isalpha() else False, text)))
    upper = np.sum(list(map(lambda character: character.isupper() if character.isalpha() else False, text)))
    values = [alphabetic/total,
              numeric/total,
              punctuation/total,
              space/total,
              lower/(alphabetic+1),
              upper/(alphabetic+1)]
    labels = ['alphabetic',
              'numeric',
              'punctuation',
              'space',
              'lower',
              'upper']
    return values, labels

def sentence_level(text):
    sentences = sent_tokenize(text)
    if len(sentences) > 0:
        avg_tokens = np.mean([len(word_tokenize(sentence)) for sentence in sentences])
    else:
        avg_tokens = 0
    return [len(sentences), avg_tokens], ['num_sentences','avg_tokens']


def POS_frequency(text):
    tags = "CC CD DT EX FW IN JJ JJR JJS LS MD NN NNP NNPS NNS PDT POS PRP PRP$ RB RBR RBS RP SYM TO UH VB VBD VBG VBN VBP VBZ WDT WP WP$ WRB"
    tags_occurrences = dd(int)
    total = 1
    for _, tag in pos_tag(word_tokenize(text)):
        tags_occurrences[tag]+=1
        total+=1
    return [tags_occurrences[tag]/total for tag in tags.split()], tags.split()