import requests
from bs4 import BeautifulSoup

from common import config


class NewsPage:
    def __init__(self, news_site_uid, url):
        self._config = config()['news_sites'][news_site_uid]
        self._queries = self._config['queries']
        self._html = None

        self._visit(url)

    def _select(self, query_string):
        return self._html.select(query_string)

    def _visit(self, url):
        response = requests.get(url)

        response.raise_for_status()

        self._html = BeautifulSoup(response.text, 'html.parser')


class HomePage(NewsPage):
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)

    @property
    def article_links(self):
        link_list = [
            link
            for link in self._select(self._queries['homepage_article_links'])
            if link and link.has_attr('href')
        ]

        return set(link['href'] for link in link_list)


class ArticlePage(NewsPage):
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)

    @property
    def title(self):
        result = self._select(self._queries['article_title'])

        return result[0].text.strip() if len(result) else ''

    @property
    def body(self):
        result = self._select(self._queries['article_body'])

        return result[0].text.strip() if len(result) else ''
