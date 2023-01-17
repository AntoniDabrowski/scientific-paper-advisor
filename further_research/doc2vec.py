from sentence_transformers import SentenceTransformer
from transformers import TFDPRQuestionEncoder, DPRQuestionEncoderTokenizer
import tensorflow as tf
from tqdm.auto import tqdm
import numpy as np

DPRQ_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
DPRQ_model = TFDPRQuestionEncoder.from_pretrained("facebook/dpr-question_encoder-single-nq-base", from_pt=True)
SentenceTransformerModel = SentenceTransformer('all-MiniLM-L6-v2')


def artificial_padding(documents_tokens):
    max_words = max([documents_token.shape[1] for documents_token in documents_tokens])
    return tf.concat(
        [tf.concat([documents_token, tf.zeros([1, max_words - documents_token.shape[1]], dtype=tf.int32)], 1) for
         documents_token in documents_tokens], 0)


def doc2vec(docs, model='document transformer'):
    article_ids = list(docs.keys())
    article_bodies = list(docs.values())

    if model == 'sentence transformer':
        # Loading model
        embeddings = SentenceTransformerModel.encode(article_bodies)
    elif model == 'document transformer':
        # demonstrational purposes / won't work online
        embeddings = np.array([]).reshape(0, 768)
        for i in tqdm(range(0, len(article_bodies), 50)):
            embeddings_batch = [DPRQ_tokenizer(article, return_tensors="tf")["input_ids"] for article in
                                article_bodies[i:i + 50]]
            embeddings_batch = artificial_padding(embeddings_batch)
            embeddings_batch = DPRQ_model(embeddings_batch).pooler_output.numpy()
            embeddings = np.vstack([embeddings, embeddings_batch])
    else:
        pass
    return article_ids, embeddings
