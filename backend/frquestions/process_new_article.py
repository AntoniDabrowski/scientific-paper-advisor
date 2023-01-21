import pickle
# from sentence_transformers import SentenceTransformer
from os import listdir
from os.path import join
import pandas as pd
import re

from frquestions.category_analysis.model import predict_category
from frquestions.models import ProcessedPDF


def split_into_sentences(text):
    # Fast way to split text into sentences
    # handles many of the more painful edge cases
    # that make sentence parsing non-trivial
    # D Greenberg
    # https://stackoverflow.com/questions/4576077/how-can-i-split-a-text-into-sentences
    alphabets = "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"
    digits = "([0-9])"

    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    if "..." in text: text = text.replace("...", "<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
    if "”" in text: text = text.replace(".”", "”.")
    if "\"" in text: text = text.replace(".\"", "\".")
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


def contain_phrase(sentence):
    return any([True for phrase in ['further research', 'further study'] if phrase in sentence])


def parse_hovers(docs):
    hovers = []

    for doc in docs:
        new_doc = ""
        current_line = ""
        for word in doc.split():
            if len(current_line) + len(word) > 60:
                new_doc += current_line + '<br>'
                current_line = ""
            current_line += ' ' + word
        if current_line:
            new_doc += current_line + '<br>'
        hovers.append(new_doc)
    return hovers


def extract_FR(section):
    sentences = split_into_sentences(section)
    if contain_phrase(sentences[0]):
        return ' '.join(sentences[:2])
    if contain_phrase(sentences[-1]):
        return ' '.join(sentences[-2:])
    for i in range(1, len(sentences) - 1):
        if contain_phrase(sentences[i]):
            return ' '.join(sentences[i - 1:i + 2])


def handle_PDF_response(response):
    all_sections = []
    further_research = ""
    for section in response['sections']:
        for text in section.values():
            all_sections.append(text)
            if contain_phrase(text):
                further_research = extract_FR(text)

    all_sections = '\n'.join(all_sections)
    return all_sections, further_research


def get_model(category):
    mypath_input = './frquestions/models'
    for f in listdir(mypath_input):
        if category == f[:len(category)]:
            return pickle.load(open(join(mypath_input, f), 'rb'))


def get_csv(category):
    mypath_input = './frquestions/results_processed'
    for f in listdir(mypath_input):
        if category == f[:len(category)]:
            return pd.read_csv(join(mypath_input, f))


def pipeline(from_pdf, from_db, url):
    if not from_pdf and not from_db:
        return {}
    if from_pdf:
        article_text, further_research_section = handle_PDF_response(from_pdf)
        category = predict_category(article_text)
    else:
        category = from_db['title']
        further_research_section = None

    # Loading PCA model and data from category
    model = get_model(category)
    df = get_csv(category)
    x, y, z = df['x'].tolist(), df['y'].tolist(), df['z'].tolist()
    cluster = df['cluster'].tolist()

    # TODO: Add url to PDFs in *.csv files
    if 'url' in df.columns:
        urls = df['url'].tolist()
    else:
        urls = ["https://arxiv.org/pdf/1712.05855.pdf"] * len(x)

    hovers = []

    for _, record in df.iterrows():
        hover = record['further research prefix'] + ' ' if type(record['further research prefix']) == str else ""
        hover += record['further research line'] + ' ' if type(record['further research line']) == str else ""
        hover += record['further research suffix'] + ' ' if type(record['further research suffix']) == str else ""
        hovers.append(hover)

    if from_pdf and further_research_section:
        # SentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')
        # embedding = SentenceTransformerModel.encode([further_research_section])
        # _x, _y, _z = model.transform(embedding)[0]
        _x, _y, _z = (0.3,0.3,0.3)
        x.append(_x)
        y.append(_y)
        z.append(_z)
        cluster.append("CURRENT")
        hovers.append(further_research_section)
        urls.append(url)

    hovers = parse_hovers(hovers)

    empty_cluster = lambda color: {"x": [], "y": [], "z": [], "text": [], "url": urls, "title": category,
                                   "color": color}
    traces = {"A": empty_cluster('rgb(255, 150, 150)'),
              "B": empty_cluster('rgb(150, 255, 150)'),
              "C": empty_cluster('rgb(150, 150, 255)'),
              "A_centroid": empty_cluster('red'),
              "B_centroid": empty_cluster('green'),
              "C_centroid": empty_cluster('blue')}
    if further_research_section:
        traces["CURRENT"] = empty_cluster('black')

    for _x, _y, _z, _cluster, _hover, _url in zip(x, y, z, cluster, hovers, urls):
        traces[_cluster]['x'].append(str(_x))
        traces[_cluster]['y'].append(str(_y))
        traces[_cluster]['z'].append(str(_z))
        traces[_cluster]['text'].append(_hover)
        traces[_cluster]['url'].append(_url)

        if from_pdf and _cluster == "CURRENT":
            ProcessedPDF.objects.create(url=_url,
                                        x=_x,
                                        y=_y,
                                        z=_z,
                                        category=category,
                                        hover=_hover)

    if from_db:
        traces["CURRENT"] = from_db

    return traces


if __name__ == '__main__':
    import json

    partially_parsed_PDF = json.load(open('partially_parsed_pdf.json', 'r'))
    url = "http://www.csjournals.com/IJITKM/PDF%203-1/55.pdf"
    parsed_PDF = pipeline(partially_parsed_PDF, url)
    json.dump(parsed_PDF, open('parsed_pdf.json', 'w'))
