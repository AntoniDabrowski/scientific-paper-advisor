import pickle

KNN_model = pickle.load(open('frquestions/category_analysis/model.pickle', 'rb'))

def predict_category(article_text,SentenceTransformer_loaded):
    embedding = SentenceTransformer_loaded.encode([article_text])
    return KNN_model.predict(embedding)[0]