import requests
import os
import shutil
import concurrent.futures
import html
import json
import datetime

from models import Posts, Base, Tag
from models import session
from utilities import escapeString
import ddInterface

from sources.gelbooru import gelbooru_api

class moebooru_base:
    '''
    Lets consolidate our interaction with the booru api into a nice
    class so we don't have to stare at a bunch of messy code.
    '''

    base_url = None
    thumb_url = None
    json_api = None
    post_dict = {}

    tag_types = {1:'artist', 3:'copyright', 4:'character'}

    def __init__():
        pass

    @classmethod
    def archive(cls, post):
        '''
        Lazy moebooru archive function adds a post to our
        db and moves the image to our dump area.
        '''
        if isinstance(post.get('tags'), list):
            etags = [escapeString(tag) for tag in post.get('tags')]
            post['tags'] = ' '.join(etags)

        tags = '|{}|'.format(post.get('tags').replace(' ', '|'))
        local_path = ''
        archive_path = ''

        filename = '{}.{}'.format(post.get('md5'), post.get('file_ext'))
        local_path = 'gazer/static/temp/{}'.format(filename)
        archive_path = 'gazer/static/dump/{}/{}/{}'.format(post.get('md5')[:2], post.get('md5')[2:4], filename)
        parsed_date = datetime.datetime.fromtimestamp(post.get('created_at'))
        parsed_date = int(parsed_date.strftime("%Y%m%d%H%M%S"))

        dd_tags = ddInterface.evaluate(local_path)
        dd_tags = ddInterface.union(tags=post.get('tags'), dd_tags=dd_tags)

        new_post = Posts(
            filename='{}.{}'.format(post.get('md5'),post.get('file_ext')),
            id=post.get('id'),
            booru=cls.source,
            source=post.get('source'),
            score=post.get('score'),
            tags=tags,
            dd_tags=dd_tags,
            rating=post.get('rating'),
            status=post.get('status'),
            created_at=parsed_date,  # moebooru uses timestamps
            creator_id=post.get('creator_id')
            )
        session.add(new_post)
        session.commit()

        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        shutil.copyfile(local_path, archive_path)

        return new_post.id

    @classmethod
    def cached_post(cls, id=None):
        if id:
            return cls.post_dict.get(int(id))
        return None

    @classmethod
    def get_post(cls, id):
        post = cls.cached_post(id)

        post['file'] = 'static/temp/{}.{}'.format(post.get('md5'), post.get('file_ext'))
        filepath = 'gazer/{}'.format(post['file'])

        if not os.path.exists(filepath):
            response = requests.get(post.get('jpeg_url'), stream=True)
            with open(filepath, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response

        # if tags are a string make them a list
        if isinstance(post['tags'], str):
            post['tags'] = post['tags'].split()

        return post

    @classmethod
    def get_posts(cls, tags=None, limit=100, page=0):
        '''
        Grab post json from the moebooru api
        Moebooru api page starts from 1
        '''
        tags = ' '.join(tags)
        url = "{}/{}?tags={}&limit={}&page={}"\
                .format(cls.base_url, cls.json_api, tags, limit, page+1)
        response = requests.get(url)

        # gelbooru api does not return empty json list properly
        if response.text:
            # give each post an image property for compatiblity with scraper
            posts = json.loads(html.unescape(response.text))
            for post in posts:
                post['image'] = '{}.{}'.format(post.get('md5'), post.get('file_ext'))

            # hack lookup table to get around moebooru api issues
            cls.post_dict = {post['id']:post for post in posts}

            return posts
        else:
            return []

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
    def download_thumbnail(cls, url=None, local_path_thumb=None):
        '''
        Download a specified thumbnail to the local path
        '''

        if not os.path.exists(local_path_thumb):
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(local_path_thumb, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                return "successful thumbnail download"
            else:
                return "thumbnail download failed"

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
                # we may need to change this file structure if folder gets saturated
                local_path_thumb = 'gazer/static/temp/thumb_{}.jpg'.format(post.get('md5'))
                url = "{}/{}/{}/{}.jpg"\
                        .format(cls.thumb_url, post.get('md5')[:2], post.get('md5')[2:4], post.get('md5'))
                futures.append(executor.submit(cls.download_thumbnail, url=url, local_path_thumb=local_path_thumb))

                # may need some error handling here
                post['thumbnail'] = 'static/temp/thumb_{}.jpg'.format(post.get('md5'))

            # just some debug stuff for now
            for future in concurrent.futures.as_completed(futures):
                future.result()

        return posts
