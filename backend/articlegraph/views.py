import unicodedata
from typing import List, Union

import networkx as nx
from django.http import HttpRequest, JsonResponse
from scholarly import scholarly, Publication, ProxyGenerator

pg = ProxyGenerator()
success = pg.ScraperAPI("6312b33d8af2fa7e8e30579203d3ab63")
print("Success:{}".format(success))
scholarly.use_proxy(pg)


class ArticleGraph(nx.Graph):
    def __init__(self, core_article: Publication, max_articles_per_column: int = 5, **attr):
        super().__init__(**attr)
        self.core_article = core_article
        self.max_articles_per_column = max_articles_per_column
        self.add_article_node(0, self.core_article)
        self.create_right_side_of_graph()

    def create_right_side_of_graph(self):
        core_article_cites = scholarly.citedby(scholarly.fill(self.core_article))
        if core_article_cites.total_results is not None:
            core_article_cites = [next(core_article_cites) for _ in
                                  range(min([core_article_cites.total_results, self.max_articles_per_column]))]
            core_article_cites = sorted(core_article_cites,
                                        key=lambda x: x.get('num_citations', 0), reverse=True)
            start_idx = self.number_of_nodes()
            for i, article in enumerate(core_article_cites):
                self.add_article_node(start_idx + i, article, 0)

    def add_article_node(self, idx, article: Publication, article_from=None):
        self.add_node(idx,
                      title=article['bib']['title'],
                      authors=article['bib']['author'],
                      num_publications=article['num_citations'],
                      url=article['pub_url'])
        if article_from is not None:
            self.add_edge(idx, article_from)


def articles_match(publication_dict, authors, title):
    publication_authors = publication_dict['author']
    publication_authors.sort()

    return title == publication_dict['title'] and authors == publication_authors


def find_article(title: str, authors: List[str]) -> Union[Publication, None]:
    # query need to reflect what we put into the Google Scholar search bar.
    query = title + " " + " ".join(["author:\"{}\"".format(author) for author in authors])
    publication_generator = scholarly.search_pubs(query=query)

    authors.sort()  # We sort here not to repeat on each articles_match
    for publication in publication_generator:
        if articles_match(publication.get('bib'), authors, title):
            # Use api to find an article with matching title and authors list.
            return publication

    # Matching article wasn't found.
    return None


def index(request: HttpRequest):
    authors = request.GET.get('authors').split(',')
    authors = [unicodedata.normalize('NFKD', a).strip() for a in authors]
    title = request.GET.get('title')

    article = find_article(title, authors)
    graph_schema = ArticleGraph(article)
    json_graph = nx.node_link_data(graph_schema)

    return JsonResponse(json_graph)
