import re
from datetime import datetime
import csv
import argparse
import logging
from typing import Union

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

from interfaces import HomePage, ArticlePage
from common import config


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')


def _news_scraper(news_site_uid: str) -> None:
    host = config()['news_sites'][news_site_uid]['url']

    logging.info(f'Beginning scraper for {host}')
    homepage = HomePage(news_site_uid, host)

    articles = []

    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info('Article fetched!!')
            articles.append(article)

    _save_articles(news_site_uid, articles)


def _build_link(host: str, link: str) -> str:
    return link if is_well_formed_link.match(link) \
        else f'{host}{link}' if is_root_path.match(link) \
        else f'{host}/{link}'


def _fetch_article(news_site_uid: str, host: str, link: str) -> Union[ArticlePage, None]:
    logger.info(f'Start fetching article at {link}')

    article = None

    try:
        article = ArticlePage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as error:
        logger.warning('Error while fetching the article', exc_info=False)

    if article and not article.body:
        logger.warning('Invalid article. There is no body')
        return None

    return article


def _save_articles(news_site_uid: str, articles: list[ArticlePage]) -> None:
    current_date = datetime.now().strftime('%Y-%m-%d')
    out_file_name = f'{news_site_uid}_{current_date}_articles.csv'

    csv_headers = list(filter(
        lambda property: not property.startswith('_'),
        dir(articles[0]))
    )

    with open(out_file_name, mode='w+', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article, header)) for header in csv_headers]
            writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_sites_choices = list(config()['news_sites'].keys())
    parser.add_argument(
        'news_site',
        help='The news site that you want to scrape',
        type=str,
        choices=news_sites_choices
    )

    args = parser.parse_args()
    _news_scraper(args.news_site)
