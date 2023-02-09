import os

import nltk
from django.apps import AppConfig
from dotenv import load_dotenv
from scholarly import ProxyGenerator, scholarly


def prepare_nltk():
    try:
        nltk.data.find('punkt')
        nltk.data.find('averaged_perceptron_tagger')
    except LookupError:
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')


class ArticlegraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articlegraph'

    def ready(self):
        load_dotenv()

        pg = ProxyGenerator()
        success = pg.ScraperAPI(os.getenv('SCRAPERAPI_KEY'))
        print("Proxy setup success:{}".format(success))
        scholarly.use_proxy(pg)

        prepare_nltk()
