import copy
import json
import multiprocessing
import os
import tempfile
import unicodedata
from datetime import date, timedelta
from multiprocessing import Process
from pathlib import Path
from typing import List, Dict

import networkx as nx
import requests
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from networkx import node_link_graph
from scholarly import scholarly, Publication
from science_parse_api.api import parse_pdf
from unidecode import unidecode

from .models import ScholarlyPublication, CitationReferences, FailedPublicationGrab
from .popularity_prediction.model import predict


def normalize_authors_list(authors_list: List[str]):
    authors_list = [unidecode(author).lower().split()[-1] for author in authors_list]
    return authors_list


class PublicationWithID:
    def __init__(self, pk=None, idx: int = None, publication: Publication = None):
        if pk is not None:
            self.from_pk(pk)
        elif idx is not None and publication is not None:
            self.idx = idx
            self.publication = publication
        else:
            raise ValueError

    def from_pk(self, pk):
        record = ScholarlyPublication.objects.get(pk=pk)

        self.idx = record.pk
        self.publication = record.publication


def add_publication_to_database(publication: Publication, cites: ScholarlyPublication = None):
    authors = normalize_authors_list(publication['bib'].get('author'))

    try:
        record = ScholarlyPublication.objects.get(title=publication['bib'].get('title').lower())
    except ScholarlyPublication.DoesNotExist:
        record = ScholarlyPublication.objects.create(title=publication['bib'].get('title').lower(),
                                                     authors=authors,
                                                     publication=publication)
    else:
        record.title = publication['bib'].get('title').lower()
        record.authors = authors
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
    def __init__(self, core_article: PublicationWithID = None, schema=None, max_articles_per_column: int = 5, **attr):
        super().__init__(**attr)
        self.core_article = None
        self.max_articles_per_column = max_articles_per_column

        if schema is not None:
            self.init_from_schema(schema)
        elif core_article is not None:
            self.init_from_article(core_article)
        else:
            raise RuntimeError

    def init_from_schema(self, schema: dict):
        node_graph = node_link_graph(schema)
        self.add_nodes_from([(n, attributes) for (n, attributes) in node_graph.nodes.items()])
        self.add_edges_from(node_graph.edges)

    def init_from_article(self, core_article: PublicationWithID):
        self.core_article = core_article
        self.add_article_node(self.core_article.idx, self.core_article.publication, subset=0)
        self.create_right_side_of_graph()
        self.create_left_side_of_graph()

    def get_citedby(self, article: PublicationWithID) -> List[PublicationWithID]:
        already_used = set()

        db_record_of_publication = ScholarlyPublication.objects.get(pk=article.idx)

        query_set_publications = CitationReferences.objects.filter(cites_id=article.idx).values()
        results = []
        for result in query_set_publications:
            citing_pub = ScholarlyPublication.objects.get(pk=result['article_id_id'])
            results.append(PublicationWithID(idx=citing_pub.id, publication=citing_pub.publication))

        already_used.update([r.publication['bib'].get('title') for r in results])

        if len(results) < self.max_articles_per_column:
            core_article = article.publication
            if core_article.get('citedby_url') is None:
                return results
            core_article_cites = scholarly.citedby(core_article)
            while len(results) < self.max_articles_per_column:
                try:
                    next_publication = next(core_article_cites)
                    if next_publication['bib'].get('title') not in already_used:
                        article_with_id = add_publication_to_database(publication=next_publication,
                                                                      cites=db_record_of_publication)
                        results.append(article_with_id)

                        already_used.add(next_publication['bib'].get('title'))
                except StopIteration:
                    break

        return results

    def trim_subset(self, target_subset):
        nodes_in_second_layer = [n for n in self.nodes(data='num_publications')
                                 if self.nodes[n[0]]['subset'] == target_subset]
        nodes_in_second_layer = sorted(nodes_in_second_layer, key=lambda x: x[1])[:self.max_articles_per_column]
        nodes_in_second_layer_idx = [x[0] for x in nodes_in_second_layer]

        copy_nodes = copy.deepcopy(self.nodes)
        for n in copy_nodes:
            if self.nodes[n]['subset'] == target_subset and n not in nodes_in_second_layer_idx:
                self.remove_node(n)

    def find_graph_right_edge(self) -> (List[PublicationWithID], int):
        max_subset = max([data for _, data in self.nodes(data='subset')])
        right_edge = [nid for nid, data in self.nodes(data='subset') if data == max_subset]

        return right_edge, max_subset

    def find_graph_left_edge(self) -> (List[PublicationWithID], int):
        min_subset = min([data for _, data in self.nodes(data='subset')])
        left_edge = [PublicationWithID(pk=nid) for nid, data in self.nodes(data='subset') if data == min_subset]

        return left_edge, min_subset

    def create_right_side_of_graph(self):
        def handle_pub(pub_idx: int, queue: multiprocessing.Queue):
            pub = PublicationWithID(pk=pub_idx)
            core_article_cited_in = self.get_citedby(pub)
            core_article_cited_in = sorted(core_article_cited_in,
                                           key=lambda x: x.publication.get('num_citations', 0), reverse=True)
            queue.put((pub_idx, core_article_cited_in))

        pubs_to_expand, edge_subset = self.find_graph_right_edge()

        queue = multiprocessing.Queue()
        process_list = []
        for publ in pubs_to_expand:
            p = Process(target=handle_pub, args=(publ, queue))
            p.start()
            process_list.append(p)

        for p in process_list:
            p.join()

        while True:
            try:
                pubidx, plist = queue.get(block=False)
                for article in plist:
                    self.add_article_node(article.idx,
                                          article.publication,
                                          article_from=pubidx,
                                          subset=edge_subset + 1)

            except:
                break

        self.trim_subset(edge_subset + 1)

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
        pubs_to_expand, edge_subset = self.find_graph_left_edge()

        for pub in pubs_to_expand:
            pdf_url = pub.publication.get('eprint_url')
            if pdf_url is None:
                continue

            parsed_pdf = parse_article_pdf(pdf_url)
            references = parsed_pdf.get('references')

            if references is None:
                continue

            articles = self.articles_from_references(references)
            for article in articles:
                self.add_article_node(article.idx,
                                      article.publication,
                                      article_from=pub.idx,
                                      subset=edge_subset - 1)

        self.trim_subset(edge_subset - 1)

    def add_article_node(self, idx, article: Publication, subset: int, article_from=None, lock=None):
        if lock is not None:
            lock.acquire()

        pub_year = article['bib']['pub_year']
        num_citations = article['num_citations']
        title = article['bib']['title']
        predicted = False

        if isinstance(pub_year, int) and pub_year >= int(os.getenv('YEAR_THRESHOLD')) \
                and num_citations <= int(os.getenv('CITATION_THRESHOLD')):
            abstract = article['bib'].get('abstract', "NONE")
            num_citations = predict(title, abstract)
            predicted = True

        self.add_node(idx,
                      title=article['bib']['title'],
                      authors=article['bib']['author'],
                      num_publications=num_citations,
                      url=article.get('pub_url'),
                      predicted=predicted,
                      subset=subset)
        if article_from is not None:
            self.add_edge(idx, article_from)
        if lock is not None:
            lock.release()

    def get_publication_from_idx(self, idx) -> PublicationWithID:
        return PublicationWithID(pk=idx)


def articles_match(publication_dict, authors, title):
    publication_authors = [unidecode(a) for a in publication_dict['author']]
    publication_authors.sort()

    return title == publication_dict['title'] and authors == publication_authors


def authors_check_out(first_authors_set: List[str], other_authors_set: List[str]):
    def intersection(lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

    first_authors_set = normalize_authors_list(first_authors_set)
    other_authors_set = normalize_authors_list(other_authors_set)

    return intersection(first_authors_set, other_authors_set) != []


def find_article(title: str, authors: List[str]) -> PublicationWithID:
    """
    :param title: Title of the article.
    :param authors: List of authors of the article.
    :return:
    :raises RuntimeError: More than one record found in the database or the record couldn't
        have been found in Google Scholar.
    """
    # Check the database for stored data
    authors = normalize_authors_list(authors)
    title = title.lower()

    timeout_failed_search = date.today() - timedelta(days=int(os.getenv('TIMEOUT_OF_FAILED_SEARCH_IN_DAYS')))

    if ScholarlyPublication.objects.filter(title=title).exists():
        # Publication found. Get from the database
        print("Record for publication {} retrieved from the database.".format(title))

        db_records = ScholarlyPublication.objects.get(title=title)
        if isinstance(db_records, QuerySet):
            for potential_article in db_records:
                potential_authors = potential_article.authors
                if authors_check_out(authors, potential_authors):
                    return PublicationWithID(idx=potential_article.pk, publication=potential_article.publication)
        else:
            if authors_check_out(authors, db_records.authors):
                return PublicationWithID(idx=db_records.pk, publication=db_records.publication)

    elif FailedPublicationGrab.objects.filter(title=title,
                                              attemptdate__gte=timeout_failed_search).exists():
        # We already looked for this article and failed
        raise RuntimeError('Article {} is recorded in the database as a failed searched.'.format(title))

    # query need to reflect what we put into the Google Scholar search bar.

    print("Looking for article {} in scholarly.".format(title))
    query = title + " " + " ".join(["author:\"{}\"".format(author) for author in authors])
    publication_generator = scholarly.search_pubs(query=query)

    counter = 0
    for publication in publication_generator:
        # Use api to find an article with matching title and authors list.

        if publication['bib'].get('title', 'NOT FOUND').lower() == title.lower() \
                and authors_check_out(authors, publication['bib'].get('author', 'NOT FOUND')):
            # Save article to db for reuse.
            return add_publication_to_database(publication=publication)
        else:
            add_publication_to_database(publication=publication)  # Save any found articles

        counter += 1
        if counter == int(os.getenv('LIMIT_OF_ARTICLES_TO_SEARCH_THROUGH')):
            break

    # Matching article wasn't found.
    FailedPublicationGrab.objects.update_or_create(title=title, authors=authors)  # Record failed search attempt
    raise RuntimeError('Article not found in Scholar.')


def get_graph_as_json(article: ArticleGraph):
    json_graph = nx.node_link_data(article)
    json_graph['layout'] = {k: tuple(v) for k, v in nx.multipartite_layout(article).items()}

    return json_graph


@csrf_exempt
def expand_left(request: HttpRequest):
    sent_schema = json.loads(request.body.decode('utf-8'))
    article_graph = ArticleGraph(schema=sent_schema)
    article_graph.create_left_side_of_graph()

    graph_json_schema = get_graph_as_json(article_graph)

    return JsonResponse(graph_json_schema)


@csrf_exempt
def expand_right(request: HttpRequest):
    sent_schema = json.loads(request.body.decode('utf-8'))
    article_graph = ArticleGraph(schema=sent_schema)
    article_graph.create_right_side_of_graph()

    graph_json_schema = get_graph_as_json(article_graph)

    return JsonResponse(graph_json_schema)


def index(request: HttpRequest):
    authors = request.GET.get('authors').split(',')
    authors = [unicodedata.normalize('NFKD', a).strip() for a in authors]
    title = request.GET.get('title')

    article = find_article(title, authors)

    article_graph = ArticleGraph(core_article=article)
    graph_json_schema = get_graph_as_json(article_graph)

    return JsonResponse(graph_json_schema)
