rm -r build dist
pyinstaller --onefile --add-data 'templates:templates' --add-data 'static:static' main.py
