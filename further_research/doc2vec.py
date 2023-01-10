from sentence_transformers import SentenceTransformer
SentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')

def doc2vec(docs):
    article_ids = list(docs.keys())
    article_bodies = list(docs.values())

    embeddings = SentenceTransformerModel.encode(article_bodies)
    return article_ids, embeddings