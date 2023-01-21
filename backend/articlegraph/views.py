import os
import tempfile
import unicodedata
from pathlib import Path
from typing import List, Dict

import networkx as nx
import requests
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from dotenv import load_dotenv
from scholarly import scholarly, Publication, ProxyGenerator
from science_parse_api.api import parse_pdf
from unidecode import unidecode

from .models import ScholarlyPublication, CitationReferences

load_dotenv()

pg = ProxyGenerator()
success = pg.ScraperAPI(os.getenv('SCRAPERAPI_KEY'))
print("Proxy setup success:{}".format(success))
scholarly.use_proxy(pg)


class PublicationWithID:
    def __init__(self, idx: int, publication: Publication):
        self.idx = idx
        self.publication = publication


def add_publication_to_database(publication: Publication, cites: ScholarlyPublication = None):
    authors = sorted(publication['bib'].get('author'))
    authors_mash = "".join([unidecode(a).lower() for a in authors])

    try:
        record = ScholarlyPublication.objects.get(title=publication['bib'].get('title').lower(),
                                                  authors=authors_mash)
    except ScholarlyPublication.DoesNotExist:
        record = ScholarlyPublication.objects.create(title=publication['bib'].get('title').lower(),
                                                     authors=authors_mash,
                                                     publication=publication)
    else:
        record.title = publication['bib'].get('title').lower()
        record.authors = authors_mash
        record.publication = publication
        record.save()

    if cites is not None:
        CitationReferences.objects.get_or_create(article_id=record, cites_id=cites)

    return PublicationWithID(idx=record.pk, publication=publication)


def parse_article_pdf(pdf_url):
    host = 'http://{}'.format(os.getenv('PDFPARSER_HOST'))
    port = os.getenv('PDFPARSER_PORT')

    with tempfile.NamedTemporaryFile() as fp:
        response = requests.get(pdf_url)
        fp.write(response.content)

        output_dict = parse_pdf(host, Path(fp.name), port=port)

    return output_dict


class ArticleGraph(nx.Graph):
    def __init__(self, core_article: PublicationWithID, max_articles_per_column: int = 5, **attr):
        super().__init__(**attr)
        self.core_article = core_article
        self.max_articles_per_column = max_articles_per_column
        self.add_article_node(0, self.core_article.publication)
        self.create_right_side_of_graph()
        self.create_left_side_of_graph()

    def get_citedby(self, article: PublicationWithID) -> List[PublicationWithID]:
        already_used = set()

        db_record_of_publication = ScholarlyPublication.objects.get(pk=article.idx)

        query_set_publications = CitationReferences.objects.filter(cites_id=article.idx).values()
        results = []
        for result in query_set_publications:
            citing_pub = ScholarlyPublication.objects.get(pk=result['article_id_id'])
            results.append(PublicationWithID(citing_pub.id, citing_pub.publication))

        already_used.update([r.publication['bib'].get('title') for r in results])

        if len(results) < self.max_articles_per_column:
            core_article_cites = scholarly.citedby(scholarly.fill(article.publication))
            counter = 0
            while counter < article.publication['num_citations'] and len(results) < self.max_articles_per_column:
                next_publication = next(core_article_cites)
                if next_publication['bib'].get('title') not in already_used:
                    article_with_id = add_publication_to_database(publication=next_publication,
                                                                  cites=db_record_of_publication)
                    results.append(article_with_id)

                    counter += 1
                    already_used.add(next_publication['bib'].get('title'))

        return results

    def get_citedby(self, article: PublicationWithID) -> List[PublicationWithID]:
        already_used = set()

        db_record_of_publication = ScholarlyPublication.objects.get(pk=article.idx)

        query_set_publications = CitationReferences.objects.filter(cites_id=article.idx).values()
        results = []
        for result in query_set_publications:
            citing_pub = ScholarlyPublication.objects.get(pk=result['article_id_id'])
            results.append(PublicationWithID(citing_pub.id, citing_pub.publication))

        already_used.update([r.publication['bib'].get('title') for r in results])

        if len(results) < self.max_articles_per_column:
            core_article_cites = scholarly.citedby(scholarly.fill(article.publication))
            counter = 0
            while counter < article.publication['num_citations'] and len(results) < self.max_articles_per_column:
                next_publication = next(core_article_cites)
                if next_publication['bib'].get('title') not in already_used:
                    article_with_id = add_publication_to_database(publication=next_publication,
                                                                  cites=db_record_of_publication)
                    results.append(article_with_id)

                    counter += 1
                    already_used.add(next_publication['bib'].get('title'))

        return results

    def create_right_side_of_graph(self):
        core_article_cited_in = self.get_citedby(self.core_article)
        core_article_cited_in = sorted(core_article_cited_in,
                                       key=lambda x: x.publication.get('num_citations', 0), reverse=True)
        start_idx = self.number_of_nodes()
        for i, article in enumerate(core_article_cited_in):
            self.add_article_node(start_idx + i, article.publication, 0, subset=1)

    def articles_from_references(self, references: List[Dict]) -> List[PublicationWithID]:
        results = []
        for ref in references:
            if len(results) == self.max_articles_per_column:
                return results

            try:
                article = find_article(title=ref['title'], authors=ref['authors'])
            except RuntimeError:
                continue

            results.append(article)

        return results

    def create_left_side_of_graph(self):
        parsed_pdf = parse_article_pdf(self.core_article.publication['eprint_url'])
        references = parsed_pdf['references']

        articles = self.articles_from_references(references)
        start_idx = self.number_of_nodes()
        for i, article in enumerate(articles):
            self.add_article_node(start_idx + i, article.publication, 0, subset=-1)

    def add_article_node(self, idx, article: Publication, article_from=None, subset=0):
        self.add_node(idx,
                      title=article['bib']['title'],
                      authors=article['bib']['author'],
                      num_publications=article['num_citations'],
                      url=article.get('pub_url'),
                      subset=subset)
        if article_from is not None:
            self.add_edge(idx, article_from)


def articles_match(publication_dict, authors, title):
    publication_authors = [unidecode(a) for a in publication_dict['author']]
    publication_authors.sort()

    return title == publication_dict['title'] and authors == publication_authors


def find_article(title: str, authors: List[str]) -> PublicationWithID:
    """
    :param title: Title of the article.
    :param authors: List of authors of the article.
    :return:
    :raises RuntimeError: More than one record found in the database or the record couldn't
        have been found in Google Scholar.
    """
    # Check the database for stored data
    authors = sorted([author.replace('.', '') for author in authors])
    authors_mash = "".join([unidecode(a).lower() for a in authors])
    title = title.lower()

    if ScholarlyPublication.objects.filter(title=title, authors=authors_mash).exists():
        # Publication found. Get from the database
        print("Record for publication {} retrieved from the database.".format(title))
        db_records = ScholarlyPublication.objects.get(title=title, authors=authors_mash)
        if isinstance(db_records, QuerySet):
            raise RuntimeError('Database contain more than one result with this title and authors.')
        else:
            return PublicationWithID(db_records.pk, publication=db_records.publication)
    else:
        # query need to reflect what we put into the Google Scholar search bar.
        print("Looking for article {} in scholarly.".format(title))
        query = title + " " + " ".join(["author:\"{}\"".format(author) for author in authors])
        publication_generator = scholarly.search_pubs(query=query)

        for publication in publication_generator:
            # Use api to find an article with matching title and authors list.
            if publication['bib'].get('title', 'NOT FOUND').lower() == title.lower():
                # Save article to db for reuse.
                return add_publication_to_database(publication=publication)

    # Matching article wasn't found.
    raise RuntimeError('Article not found in Scholar.')


def get_graph_as_json(article: PublicationWithID):
    graph_schema = ArticleGraph(article)
    json_graph = nx.node_link_data(graph_schema)
    json_graph['layout'] = {k: tuple(v) for k, v in nx.multipartite_layout(graph_schema).items()}

    return json_graph


def index(request: HttpRequest):
    authors = request.GET.get('authors').split(',')
    authors = [unicodedata.normalize('NFKD', a).strip() for a in authors]
    title = request.GET.get('title')

    article = find_article(title, authors)
    graph_json_schema = get_graph_as_json(article)

    return JsonResponse(graph_json_schema)
