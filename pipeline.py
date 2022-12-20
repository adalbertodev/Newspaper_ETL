import logging
import subprocess

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

news_sites_uids = ['eluniversal', 'elpais']


def main() -> None:
    _extract()
    _transform()
    _load()


def _extract() -> None:
    logger.info('Starting extract process')

    for news_site_uid in news_sites_uids:
        subprocess.run(['python', 'main.py', news_site_uid], cwd='./extract')
        subprocess.run(
            ['move', f'./{news_site_uid}*.csv',
                f'../transform/{news_site_uid}_.csv'],
            cwd='./extract',
            shell=True
        )


def _transform() -> None:
    logger.info('Starting transform process')

    for news_site_uid in news_sites_uids:
        dirty_data_filename = f'{news_site_uid}_.csv'
        clean_data_filename = f'clean_{dirty_data_filename}'

        subprocess.run(
            ['python', 'main.py', dirty_data_filename],
            cwd='./transform'
        )
        subprocess.run(
            ['del', dirty_data_filename],
            cwd='./transform',
            shell=True
        )
        subprocess.run(
            ['move', clean_data_filename,
             f'../load/{news_site_uid}.csv'],
            cwd='./transform',
            shell=True
        )


def _load() -> None:
    logger.info('Starting load process')

    for news_sites_uid in news_sites_uids:
        clean_data_filename = f'{news_sites_uid}.csv'

        subprocess.run(
            ['python', 'main.py', clean_data_filename],
            cwd='./load'
        )
        subprocess.run(
            ['del', clean_data_filename],
            cwd='./load',
            shell=True
        )


if __name__ == '__main__':
    main()
