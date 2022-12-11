import argparse
import hashlib
import logging
from urllib.parse import urlparse
import nltk
from nltk.corpus import stopwords
import pandas as pd

nltk.download('punkt')
nltk.download('stopwords')

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def main(filename: str) -> None:
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)

    if df['title'].isnull().values.any():
        df = _fill_missing_titles(df)

    df = _generate_uids_for_rows(df)
    df = _remove_new_lines_from_body(df)
    df = _tokenize_columns(df, 'title')
    df = _tokenize_columns(df, 'body')
    df = _remove_duplicates_entries(df, 'title')
    df = _drop_rows_with_missing_values(df)

    _save_data(df, filename)


def _read_data(filename: str) -> pd.DataFrame:
    logger.info(f'Reading file {filename}')

    return pd.read_csv(filename)


def _extract_newspaper_uid(filename: str) -> str:
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('/')[-1].split('_')[0]

    logger.info(f'Newspaper uid detected: {newspaper_uid}')
    return newspaper_uid


def _add_newspaper_uid_column(df: pd.DataFrame, newspaper_uid: str) -> pd.DataFrame:
    logger.info(f'Filling newspaper_uid column with {newspaper_uid}')
    df['newspaper_uid'] = newspaper_uid

    return df


def _extract_host(df: pd.DataFrame):
    logger.info('Extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


def _fill_missing_titles(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Filling missing titles')

    missing_titles_mask = df['title'].isna()
    missing_titles = df[missing_titles_mask]['url'] \
        .str.extract(r'(?P<missing_titles>[^\/]+)$') \
        .applymap(lambda title: title.split('-')) \
        .applymap(lambda title_word_list: ' '.join(title_word_list))

    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']

    return df


def _generate_uids_for_rows(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Generating uid for each row')

    uids = df \
        .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1) \
        .apply(lambda hash_object: hash_object.hexdigest())

    df['uid'] = uids

    return df.set_index('uid')


def _remove_new_lines_from_body(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Removing new lines from body')

    stripped_body = df \
        .apply(lambda row: row['body'].replace('\n', ''), axis=1)

    df['body'] = stripped_body

    return df


def _tokenize_columns(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    stop_words = set(stopwords.words('spanish'))

    df[f'n_tokens_{column_name}'] = df \
        .dropna() \
        .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1) \
        .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens))) \
        .apply(lambda tokens: list(map(lambda token: token.lower(), tokens))) \
        .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list))) \
        .apply(lambda valid_word_list: len(valid_word_list))

    return df


def _remove_duplicates_entries(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    logger.info('Removing duplicate entries')

    df.drop_duplicates(subset=[column_name], keep='first', inplace=True)

    return df


def _drop_rows_with_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Dropping rows with missing values')

    return df.dropna()


def _save_data(df: pd.DataFrame, filename: str) -> None:
    clean_filename = f'clean_{filename.split("/")[-1]}'

    logger.info(f'Saving data at location: {clean_filename}')
    df.to_csv(clean_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename',
        help='The path to the dirty data',
        type=str
    )

    args = parser.parse_args()
    main(args.filename)
