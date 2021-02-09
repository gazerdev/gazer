import requests
import os
import shutil
import concurrent.futures

from models import Posts, Tag, Base, PostStat, TagStat
from models import session

class gelbooru_base:
    '''
    Lets consolidate our interaction with the booru api into a nice
    class so we don't have to stare at a bunch of messy code.
    '''

    base_url = None
    thumb_url = None
    json_api = None

    def __init__():
        pass

    @classmethod
    def archive(cls, post):
        '''
        Lazy gelbooru archive function adds a post to our
        db and moves the image to our dump area.
        '''
        if isinstance(post.get('tags'), list):
            post['tags'] = ' '.join(post.get('tags'))

        tags = '|{}|'.format(post.get('tags').replace(' ', '|'))
        local_path = ''
        archive_path = ''

        # we should change this to preserve the original source as well as
        # labelling where it came from
        new_post = Posts(
            filename=post.get('image'),
            id=post.get('id'),
            source=cls.source,
            score=post.get('score'),
            tags=tags,
            rating=post.get('rating'),
            status=post.get('status'),
            created_at=post.get('created_at'),
            creator_id=post.get('creator_id')
            )
        session.merge(new_post)
        session.flush()
        new_post_stat = PostStat(
            post_filename=new_post.filename,
            post_id=new_post.id
        )
        session.merge(new_post_stat)
        session.commit()

        local_path = 'static/temp/{}'.format(post.get('image'))
        archive_path = 'static/dump/{}/{}/{}'.format(post.get('image')[:2], post.get('image')[2:4], post.get('image'))

        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        shutil.copyfile(local_path, archive_path)

        return new_post.id

    @classmethod
    def get_post(cls, id):
        url = "{}/index.php?page=dapi&s=post&q=index&json=1&id={}".format(cls.base_url, id)
        response = requests.get(url)
        post = response.json()[0]

        post['file'] = 'static/temp/{}'.format(post.get('image'))

        if not os.path.exists(post['file']):
            response = requests.get(post.get('file_url'), stream=True)
            with open(post['file'], 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response

        # if tags are a string make them a list
        if isinstance(post['tags'], str):
            post['tags'] = post['tags'].split()

        return post

    @classmethod
    def get_posts(cls, tags=None, limit=100, page=0):
        '''
        Grab post json from the gelbooru api
        '''
        tags = ' '.join(tags)
        url = "{}/{}&tags={}&limit={}&pid={}"\
                .format(cls.base_url, cls.json_api, tags, limit, page)
        response = requests.get(url)

        # gelbooru api does not return empty json list properly
        if response.text:
            return response.json()
        return []

    @classmethod
    def get_tags(cls, tags=None):
        '''
        Grab tag data from the API
        '''
        tags = ' '.join(tags)
        url = "{}/index.php?page=dapi&s=tag&q=index&json=1&names={}".format(cls.base_url, tags)
        response = requests.get(url)

        if response.text:
            return response.json()
        return []

    @classmethod
    def serialize_tags(cls, tags=None):
        serialized_tags = {'artist':[], 'character':[], 'copyright':[], 'tag':[]}
        #tags = cls.get_tags(tags)

        for tag in tags:
            if tag.get('type') == 'artist':
                serialized_tags['artist'].append(tag)
            elif tag.get('type') == 'character':
                serialized_tags['character'].append(tag)
            elif tag.get('type') == 'copyright':
                serialized_tags['copyright'].append(tag)
            else:
                serialized_tags['tag'].append(tag)

        return serialized_tags

    @classmethod
    def save_tags(cls, tags=None):
        '''
        Save tag data to the database
        '''
        for tag in tags:
            new_tag = Tag(tag=tag.get('tag'), count=tag.get('count'),
                          type=tag.get('type'), ambiguous=tag.get('ambiguous'))
            new_tag_stat = TagStat(tag=tag.get('tag'))
            session.merge(new_tag)
            session.merge(new_tag_stat)

        session.commit()

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
                local_path_thumb = 'static/temp/thumb_{}.jpg'.format(post.get('hash'))
                url = "{}/{}/thumbnail_{}.jpg"\
                        .format(cls.thumb_url, post.get('directory'), post.get('hash'))
                futures.append(executor.submit(cls.download_thumbnail, url=url, local_path_thumb=local_path_thumb))

                # may need some error handling here
                post['thumbnail'] = local_path_thumb

            # just some debug stuff for now
            for future in concurrent.futures.as_completed(futures):
                future.result()

        return posts
