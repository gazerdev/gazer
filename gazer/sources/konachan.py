from gazer.sources.moebooru_base import moebooru_base

class konachan_api(moebooru_base):
    '''
    Lets consolidate our interaction with the booru api into a nice
    class so we don't have to stare at a bunch of messy code.
    '''

    base_url = "https://konachan.com"
    source = "konachan"
    thumb_url = "https://konachan.com/data/preview"
    json_api = "post.json"
