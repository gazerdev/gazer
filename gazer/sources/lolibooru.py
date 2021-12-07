from gazer.sources.moebooru_base import moebooru_base

class lolibooru_api(moebooru_base):
    '''
    Lets consolidate our interaction with the booru api into a nice
    class so we don't have to stare at a bunch of messy code.
    '''

    base_url = "https://lolibooru.moe"
    source = "lolibooru"
    thumb_url = "https://lolibooru.moe/data/preview"
    json_api = "post.json"
