import pickle
from os import listdir
from os.path import join
import pandas as pd
import re

from frquestions.category_analysis.model import predict_category
from frquestions.models import FR_ProcessedPDF, AB_ProcessedPDF


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
            new_doc += current_line
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
    title = response.get("title", "")
    abstract = response.get("abstractText", "")
    for section in response.get('sections', []):
        for text in section.values():
            if contain_phrase(text):
                return title, abstract, extract_FR(text)
    return title, abstract, ""


def get_model(category, part):
    if part == 'further research':
        mypath_input = './frquestions/FR_models'
    elif part == 'abstract':
        mypath_input = './frquestions/AB_models'
    for f in listdir(mypath_input):
        if category == f[:len(category)]:
            return pickle.load(open(join(mypath_input, f), 'rb'))


def get_csv(category, part):
    if part == 'further research':
        mypath_input = './frquestions/FR_results'
    elif part == 'abstract':
        mypath_input = './frquestions/AB_results'

    for f in listdir(mypath_input):
        if category == f[:len(category)]:
            return pd.read_csv(join(mypath_input, f))


def get_empty_traces(category):
    empty_cluster = lambda color: {"x": [], "y": [], "z": [], "text": [], "url": [], "title": category,
                                   "color": color}

    traces = {"A": empty_cluster('rgb(255, 150, 150)'),
              "B": empty_cluster('rgb(150, 255, 150)'),
              "C": empty_cluster('rgb(150, 150, 255)'),
              "A_centroid": empty_cluster('red'),
              "B_centroid": empty_cluster('green'),
              "C_centroid": empty_cluster('blue')}
    return traces


def prepare_data_from_csv(category, part):
    df = get_csv(category, part)
    x, y, z = df['x'].tolist(), df['y'].tolist(), df['z'].tolist()
    cluster = df['label'].tolist()
    urls = df['url'].tolist()
    titles = df['title'].tolist()
    titles = parse_hovers(titles)
    hovers = df[part].tolist()
    hovers = parse_hovers(hovers)

    traces = get_empty_traces(category)

    for _x, _y, _z, _cluster, _hover, _url, title in zip(x, y, z, cluster, hovers, urls, titles):
        traces[_cluster]['x'].append(str(_x))
        traces[_cluster]['y'].append(str(_y))
        traces[_cluster]['z'].append(str(_z))
        traces[_cluster]['text'].append(f'<b>{title}</b><br>{_hover}')
        traces[_cluster]['url'].append(_url)

    return traces


def prepare_data_from_db(category):
    records = FromArxivFR.objects.filter(category=category)

    traces = get_empty_traces(category)

    for record in records:
        hover = f'<b>{record["title"]}</b><br>{parse_hovers([record["hover"]])[0]}'
        traces[record['label']]['x'].append(str(record['x']))
        traces[record['label']]['y'].append(str(record['y']))
        traces[record['label']]['z'].append(str(record['z']))
        traces[record['label']]['text'].append(hover)
        traces[record['label']]['url'].append(record['url'])

    return traces


def handle_from_pdf(record, url, SentenceTransformer_loaded):
    if not record:
        return {}

    title, abstract, further_research_section = handle_PDF_response(record)
    category = predict_category(f'{title}.\n{abstract}', SentenceTransformer_loaded)

    traces_FR = prepare_data_from_csv(category, 'further research')
    traces_AB = prepare_data_from_csv(category, 'abstract')

    if title:
        title = parse_hovers([title])[0]

    # handling further research clustering
    if further_research_section:
        if len(further_research_section) > 1500:
            further_research_section = further_research_section[:1500] + '...'
        model = get_model(category, 'further research')
        embedding = SentenceTransformer_loaded.encode([further_research_section])
        _x, _y, _z = model.transform(embedding)[0]

        hover = parse_hovers([further_research_section])[0]
        traces_FR['CURRENT'] = {'x': [str(_x)],
                                'y': [str(_y)],
                                'z': [str(_z)],
                                'text': [f'<b>{title}</b><br>{hover}'],
                                'url': [url],
                                'title': 'CURRENT',
                                'color': 'black'}

        FR_ProcessedPDF.objects.create(url=url,
                                       x=_x,
                                       y=_y,
                                       z=_z,
                                       title=title,
                                       category=category,
                                       hover=hover)
    else:
        FR_ProcessedPDF.objects.create(url=url,
                                       x=None,
                                       y=None,
                                       z=None,
                                       title=title,
                                       category=category,
                                       hover="")

    # handling abstract clustering
    if abstract:
        if len(abstract) > 1500:
            abstract = abstract[:1500] + '...'

        model = get_model(category, 'abstract')
        embedding = SentenceTransformer_loaded.encode([abstract])
        _x, _y, _z = model.transform(embedding)[0]

        hover = parse_hovers([abstract])[0]
        traces_AB['CURRENT'] = {'x': [str(_x)],
                                'y': [str(_y)],
                                'z': [str(_z)],
                                'text': [f'<b>{title}</b><br>{hover}'],
                                'url': [url],
                                'title': 'CURRENT',
                                'color': 'black'}

        AB_ProcessedPDF.objects.create(url=url,
                                       x=_x,
                                       y=_y,
                                       z=_z,
                                       title=title,
                                       category=category,
                                       hover=hover)
    else:
        AB_ProcessedPDF.objects.create(url=url,
                                       x=None,
                                       y=None,
                                       z=None,
                                       title=title,
                                       category=category,
                                       hover="")

    return {'further_research': traces_FR, 'abstract': traces_AB}


def handle_from_db(url):
    FR_record = FR_ProcessedPDF.objects.get(url=url)
    AB_record = AB_ProcessedPDF.objects.get(url=url)

    category = FR_record.category

    traces_FR = prepare_data_from_csv(category, 'further research')
    traces_AB = prepare_data_from_csv(category, 'abstract')


    if FR_record.x is not None and FR_record.y is not None and FR_record.z is not None:
        traces_FR['CURRENT'] = {'x': [str(FR_record.x)],
                             'y': [str(FR_record.y)],
                             'z': [str(FR_record.z)],
                             'text': [f'<b>{FR_record.title}</b><br>{FR_record.hover}'],
                             'url': [url],
                             'title': 'CURRENT',
                             'color': 'black'}

    if AB_record.x is not None and AB_record.y is not None and AB_record.z is not None:
        traces_AB['CURRENT'] = {'x': [str(AB_record.x)],
                             'y': [str(AB_record.y)],
                             'z': [str(AB_record.z)],
                             'text': [f'<b>{AB_record.title}</b><br>{AB_record.hover}'],
                             'url': [url],
                             'title': 'CURRENT',
                             'color': 'black'}

    return {'further_research': traces_FR, 'abstract': traces_AB}
