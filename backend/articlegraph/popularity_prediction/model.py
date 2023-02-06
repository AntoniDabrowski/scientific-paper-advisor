import pickle
import string
from collections import defaultdict as dd

import nltk
import numpy as np
from nltk import pos_tag, word_tokenize, sent_tokenize


def prepare_nltk():
    try:
        nltk.data.find('punkt')
        nltk.data.find('averaged_perceptron_tagger')
    except LookupError:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')


prepare_nltk()

popularity_prediction_model = pickle.load(open('articlegraph/popularity_prediction/pp_MLPClassifier_4.pickle', 'rb'))


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

    return values


def sentence_level(text):
    sentences = sent_tokenize(text)
    if len(sentences) > 0:
        avg_tokens = np.mean([len(word_tokenize(sentence)) for sentence in sentences])
    else:
        avg_tokens = 0
    return [len(sentences), avg_tokens]


def POS_frequency(text):
    tags = "CC CD DT EX FW IN JJ JJR JJS LS MD NN NNP NNPS NNS PDT POS PRP PRP$ RB RBR RBS RP SYM TO UH VB VBD VBG VBN VBP VBZ WDT WP WP$ WRB"
    tags_occurrences = dd(int)
    total = 1
    for _, tag in pos_tag(word_tokenize(text)):
        tags_occurrences[tag] += 1
        total += 1
    return [tags_occurrences[tag] / total for tag in tags.split()]


def predict(title="", abstract=""):
    embedding = character_level(title)
    embedding += POS_frequency(title)
    embedding += character_level(abstract)
    embedding += sentence_level(abstract)
    embedding += POS_frequency(abstract)
    return popularity_prediction_model.predict([embedding])[0]


if __name__ == "__main__":
    title = "The weighted mixed curvature of a foliated manifold"
    abstract = "The article provides the reference on tax compliance risk for bank transactions payments by businesses in the context of developing countries such as Vietnam, as tax departments are gradually modernizing the tax administration, the use of taxpayer data between tax department and banks are not good. The review of the materials examines the issues involved in the field of tax compliance risk management and to identify gaps in the study of a tax compliance risk."

    category = predict(title, abstract)
    print(category)
    # Categories
    # 0 -> cited 0 times
    # 1 -> cited 1 to 4 times
    # 2 -> cited 5 to 16 times
    # 3 -> cited more than 16 times
