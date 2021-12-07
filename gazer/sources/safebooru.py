import concurrent.futures
import requests
import os
import shutil

from gazer.sources.gelbooru_base import gelbooru_base
from gazer.sources.gelbooru import gelbooru_api

class safebooru_api(gelbooru_base):
    '''
    Lets consolidate our interaction with the booru api into a nice
    class so we don't have to stare at a bunch of messy code.
    '''

    base_url = "https://safebooru.org"
    source = "safebooru"
    thumb_url = "https://safebooru.org/thumbnails"
    json_api = "index.php?page=dapi&s=post&q=index&json=1"

    @classmethod
    def get_tags(cls, tags=None):
        '''
        Grab tag data from the API
        Moebooru tag api has issues so just ask gelbooru instead
        '''
        return gelbooru_api.get_tags(tags)

    @classmethod
    def serialize_tags(cls, tags=None):
        return gelbooru_api.serialize_tags(tags)

    @classmethod
    def save_tags(cls, tags=None):
        '''
        Save tag data to the database
        '''
        gelbooru_api.save_tags(tags)

    @classmethod
    def get_post(cls, id):
        url = "{}/index.php?page=dapi&s=post&q=index&json=1&id={}".format(cls.base_url, id)
        response = requests.get(url)
        post = response.json()[0]

        post['file'] = 'static/temp/{}'.format(post.get('image'))
        filepath = 'gazer/{}'.format(post['file'])

        if not os.path.exists(post['file']):
            image_url = '{}/images/{}/{}'.format(cls.base_url, post.get('directory'), post.get('image'))
            response = requests.get(image_url, stream=True)
            with open(filepath, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response

        # if tags are a string make them a list
        if isinstance(post['tags'], str):
            post['tags'] = post['tags'].split()

        return post

    @classmethod
    def download_thumbnails(cls, posts=None):
        '''
        Download thumbnails from the booru.
        Skip any thumbnails that we already have.
        Return posts list with new local thumb paths.
        '''
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for post in posts:
                image_name = post.get('image')[:-4]
                # we may need to change this file structure if folder gets saturated
                local_path_thumb = 'gazer/static/temp/thumb_{}.jpg'.format(post.get('hash'))
                url = "{}/{}/thumbnail_{}.jpg"\
                        .format(cls.thumb_url, post.get('directory'), image_name)
                futures.append(executor.submit(cls.download_thumbnail, url=url, local_path_thumb=local_path_thumb))

                # may need some error handling here
                post['thumbnail'] = 'static/temp/thumb_{}.jpg'.format(post.get('hash'))

            # just some debug stuff for now
            for future in concurrent.futures.as_completed(futures):
                future.result()

        return posts
