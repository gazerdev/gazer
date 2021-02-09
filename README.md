# Gazer

This is an experimental booru client and image archive tool I made to consolidate
my own image browsing and archiving habits. It combines a simple locally running
image booru with a client for browsing some of the common booru sites. (gelbooru,
yandere, konachan, etc) and has a simple scraper for automatic downloading.

## Features
Application runs in a local web server rather than as a traditional gui interface.
Can be used either locally on a single computer or accessed over a local area
network (for example from a homeserver or media pc).
### Local Booru
<img src="docs/imgs/gazer_archive.png" width="400"><p>
- mirrors all tags from source
- tag and multitag search
- viewing statistics (by image and by tag)

### Booru Client:
<img src="docs/imgs/gazer_multi_booru_client.png" width="400"><p>
- supports gelbooru and moebooru based sites
- uses locally cached images when possible (saves bandwidth)
- 1 click archiving in client

### Scraper
<img src="docs/imgs/gazer_scraper.png" width="400"><p>
- supports gelbooru and moebooru based sites
- scrape and archive posts based on any tag or set of tags

### Why not use hydrus or x other software

I found hydrus to have a lot more features than I needed. What I really wanted
was just a personally curated booru with an easy way to browse and archive new images.

## Running

Code is still very experimental so I don't have a nice packaging solution ready,
needs to be run from commandline and accessed via browser.

### Linux/Unix/Mac
Install any version of python3 then navigate to the gazer root directory and
run the following commands in your terminal client.
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Open a browser and go to
localhost:5000 or 127.0.0.1:5000

### Windows
Install any version of python3 then navigate to the gazer root directory and
run the following commands in your terminal client.
```
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Open a browser and go to
localhost:5000 or 127.0.0.1:5000
