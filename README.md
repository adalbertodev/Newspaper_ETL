# Newspaper ETL

A complete ETL pipeline using Web Scraping to get newspapers articles and load them into a sql database, in this case, a sqlite database. This project is just a practice of a complete construction of an ETL. It uses:

- Page Object Pattern for Web Srapping.
- A yaml config for selectors and host urls.
- Pandas to transform the obtained data.
- Sqlalchemy to load the cleaned data into db.

## Dependencies

- requests
- beautifulsoup4
- pandas
- pyyaml
- nltk
- sqlalchemy

```
pip install requests beautifulsoup4 pandas pyyaml nltk sqlalchemy
```

## Execute Program

```
git clone https://github.com/adalbertodev/Newspaper_ETL.git
cd ./Newspaper_ETL
python pipeline.py
```
