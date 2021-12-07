from gazer.sources.moebooru_base import moebooru_base

class yandere_api(moebooru_base):
    '''
    Lets consolidate our interaction with the booru api into a nice
    class so we don't have to stare at a bunch of messy code.
    '''

    base_url = "https://yande.re"
    source = "yandere"
    thumb_url = "https://assets.yande.re/data/preview"
    json_api = "post.json"
