from sources.gelbooru_base import gelbooru_base

class gelbooru_api(gelbooru_base):
    '''
    Lets consolidate our interaction with the booru api into a nice
    class so we don't have to stare at a bunch of messy code.
    '''

    base_url = "https://gelbooru.com"
    source = "gelbooru"
    thumb_url = "https://img1.gelbooru.com/thumbnails"
    json_api = "index.php?page=dapi&s=post&q=index&json=1"
