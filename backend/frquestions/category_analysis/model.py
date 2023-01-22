import pickle

KNN_model = pickle.load(open('model.pickle', 'rb'))

def predict_category(article_text,SentenceTransformer_loaded):
    embedding = SentenceTransformer_loaded.encode([article_text])
    return KNN_model.predict(embedding)[0]

if __name__=="__main__":
    from sentence_transformers import SentenceTransformer
    SentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')
    abstractText = "Genetic algorithms are considered as a search process used in computing to find exact or a approximate solution for optimization and search problems. There are also termed as global search heuristics. These techniques are inspired by evolutionary biology such as inheritance mutation, selection and cross over. These algorithms provide a technique for program to automatically improve their parameters. This paper is an introduction of genetic algorithm approach including various applications and described the integration of genetic algorithm with object oriented programming approaches."
    title = "GENETIC ALGORITHM: REVIEW AND APPLICATION"
    print(predict_category(f"{abstractText}.\n{title}", SentenceTransformerModel))