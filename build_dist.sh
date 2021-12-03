rm -r build dist
pyinstaller --onefile --add-data 'gazer/templates:templates' --add-data 'gazer/static:static' gazer/__main__.py
