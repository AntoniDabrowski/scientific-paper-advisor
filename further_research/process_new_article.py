import pickle
from sentence_transformers import SentenceTransformer
from os import listdir
from os.path import join
import pandas as pd

from category_analysis.model import predict_category
from dimensionality_reduction import parse_hovers


def get_model(category):
    mypath_input = '../utils/FRDownloader/models'
    for f in listdir(mypath_input):
        if category == f[:len(category)]:
            return pickle.load(open(join(mypath_input, f),'rb'))

def get_csv(category):
    mypath_input = '../utils/FRDownloader/result_processed'
    for f in listdir(mypath_input):
        if category == f[:len(category)]:
            return pd.read_csv(join(mypath_input, f))

def pipeline(article_text, further_research_section):
    category = predict_category(article_text)

    # Loading PCA model and data from category
    model = get_model(category)
    df = get_csv(category)
    x, y, z = df['x'].tolist(), df['y'].tolist(), df['z'].tolist()
    cluster = df['cluster'].tolist()
    hovers = []

    for _, record in df.iterrows():
        hover = record['further research prefix'] + ' ' if type(record['further research prefix']) == str else ""
        hover += record['further research line'] + ' ' if type(record['further research line']) == str else ""
        hover += record['further research suffix'] + ' ' if type(record['further research suffix']) == str else ""
        hovers.append(hover)


    SentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = SentenceTransformerModel.encode([further_research_section])
    _x, _y, _z = model.transform(embedding)[0]

    x.append(_x)
    y.append(_y)
    z.append(_z)
    cluster.append("CURRENT")
    hovers.append(further_research_section)
    hovers = parse_hovers(hovers)

    export = {'x':x,
              'y':y,
              'z':z,
              'cluster':cluster,
              'hovers':hovers,
              'title':category}

    return export

