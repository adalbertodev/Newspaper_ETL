from .NewsPage import NewsPage


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
