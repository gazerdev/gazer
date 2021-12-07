rm -r build dist
pyinstaller --name gazer-server --add-data 'gazer/templates:gazer/templates' --add-data 'gazer/static:gazer/static' --add-data 'gazer/scraper_data:gazer/scraper_data' run.py