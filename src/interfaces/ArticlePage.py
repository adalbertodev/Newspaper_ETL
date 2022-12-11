from .NewsPage import NewsPage


class ArticlePage(NewsPage):
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)
        self.url = url

    @property
    def title(self):
        result = self._select(self._queries['article_title'])

        return result[0].text.strip() if len(result) else ''

    @property
    def body(self):
        result = self._select(self._queries['article_body'])

        return result[0].text.strip() if len(result) else ''
