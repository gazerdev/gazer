from flask import Flask, render_template, request, abort
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import json
import requests
import shutil
import os
from multiprocessing import Process
from scraper import scraper_run

from sources.gelbooru import gelbooru_api
from sources.yandere import yandere_api
from sources.konachan import konachan_api
from sources.lolibooru import lolibooru_api
from sources.safebooru import safebooru_api

# clean out temp directory when we start
shutil.rmtree('static/temp')
os.mkdir('static/temp')

app = Flask(__name__)

from models import Posts, PostStat, Tag, Base, TagStat
from models import session

def tagSearch(tags, limit=None, page=None, service=None):
    '''
    Search for a list of tags in database using string LIKE method
    relies on pipe delimited tag list and string search. Not as optimized
    as I would like but linear worst case so maybe ok for our small
    local server.
    '''

    if service == 'archive':
        if not tags:
            results = session.query(Posts).order_by(desc('id')).limit(limit).offset(limit*page).all()
            return [post.as_dict() for post in results]
        else:
            tag_query = ''
            for i, tag in enumerate(tags):
                if i == 0:
                    tag_query += '''tags LIKE '%|{}|%' '''.format(tag)
                else:
                    tag_query += '''AND tags LIKE '%|{}|%' '''.format(tag)

            query = '''SELECT * FROM posts
                        WHERE {}
                        ORDER BY date(created_at)
                        LIMIT {} OFFSET {}
                        '''.format(tag_query, limit, limit*page)
            results = session.execute(query)
            results = [Posts.from_tuple(r) for r in results]

            return [post.as_dict() for post in results]

    elif service == 'gelbooru':
        post_json = gelbooru_api.get_posts(tags=tags, limit=limit, page=page)
        post_json = gelbooru_api.download_thumbnails(posts=post_json)

        return post_json

    elif service == 'yandere':
        post_json = yandere_api.get_posts(tags=tags, limit=limit, page=page)
        post_json = yandere_api.download_thumbnails(posts=post_json)

        return post_json

    elif service == 'konachan':
        post_json = konachan_api.get_posts(tags=tags, limit=limit, page=page)
        post_json = konachan_api.download_thumbnails(posts=post_json)

        return post_json

    elif service == 'lolibooru':
        post_json = lolibooru_api.get_posts(tags=tags, limit=limit, page=page)
        post_json = lolibooru_api.download_thumbnails(posts=post_json)

        return post_json

    elif service == 'safebooru':
        post_json = safebooru_api.get_posts(tags=tags, limit=limit, page=page)
        post_json = safebooru_api.download_thumbnails(posts=post_json)

        return post_json

    else:
        raise Exception("undefined service type")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tags')
def tags():
    tags = session.query(TagStat).order_by(desc(TagStat.views)).all()
    tags = [stat.as_dict() for stat in tags]
    return render_template("tags.html", tags=tags)

@app.route('/tag/<name>')
def tag(name):
    tag = session.query(Tag).filter(Tag.tag==name).first()
    if tag:
        return json.dumps(tag.as_dict())
    else:
        abort(404)

@app.route('/poststats')
def poststats():
    stats = session.query(PostStat).order_by(desc(PostStat.views)).all()
    stats = [stat.as_dict() for stat in stats]
    return render_template("poststats.html", stats=stats)

@app.route('/scraper')
def scraper():
    with open("scraper_data/tag_set.json") as tags:
        tag_set = json.load(tags)
    with open("scraper_data/status.json") as status:
        current_status = json.load(status)

    return render_template("scraper.html", tag_set=tag_set, status=current_status)

@app.route('/posts')
def posts():
    page = int(request.args.get('page', 0))
    limit = int(request.args.get('limit', 20))
    service = request.args.get('service', 'archive')
    tags = request.args.get('tags', '')

    search_tags = tags.split()
    posts = tagSearch(search_tags, page=page, limit=limit, service=service)

    # easy way to handle our state is just to pass back the
    # values that the page was called with for use in our relative links
    return render_template('posts.html',
                            title='post test',
                            service=service,
                            tags=tags,
                            posts=posts,
                            page=page
                            )

# this needs some sort of cleanup getting messy
@app.route('/post/<int:id>')
def post(id):
    service = request.args.get('service', 'archive')
    tags = request.args.get('tags', '')
    archived = False
    post_tags = []

    search_tags = tags.split()

    stats = None
    if service == 'archive':
        archived = True
        post = session.query(Posts).filter(Posts.id==id).first()
        post = post.as_dict()
        serialized_tags = Tag.serialize_tags(post.get('tags'), increment_views=True)

        stats = session.query(PostStat).filter(PostStat.post_filename==post['filename']).first()
        stats.views += 1
        session.commit()
        stats = stats.as_dict()

    elif service == 'gelbooru':
        post = gelbooru_api.get_post(id)
        post_tags = gelbooru_api.get_tags(post.get('tags'))
        serialized_tags = gelbooru_api.serialize_tags(post_tags)

        if request.args.get('archive'):
            post_id = gelbooru_api.archive(post)
            gelbooru_api.save_tags(post_tags)

    elif service == 'yandere':
        post = yandere_api.get_post(id)
        post_tags = yandere_api.get_tags(post.get('tags'))
        serialized_tags = yandere_api.serialize_tags(post_tags)
        if request.args.get('archive'):
            post_id = yandere_api.archive(post)
            yandere_api.save_tags(post_tags)

    elif service == 'konachan':
        post = konachan_api.get_post(id)
        post_tags = yandere_api.get_tags(post.get('tags'))
        serialized_tags = konachan_api.serialize_tags(post_tags)
        if request.args.get('archive'):
            post_id = konachan_api.archive(post)
            konachan_api.save_tags(post_tags)

    elif service == 'lolibooru':
        post = lolibooru_api.get_post(id)
        post_tags = lolibooru_api.get_tags(post.get('tags'))
        serialized_tags = lolibooru_api.serialize_tags(post_tags)

        if request.args.get('archive'):
            post_id = lolibooru_api.archive(post)
            lolibooru_api.save_tags(post_tags)

    elif service == 'safebooru':
        post = safebooru_api.get_post(id)
        post_tags = gelbooru_api.get_tags(post.get('tags'))  # safebooru tag api is wonky use gelbooru
        serialized_tags = safebooru_api.serialize_tags(post_tags)
        if request.args.get('archive'):
            post_id = safebooru_api.archive(post)
            safebooru_api.save_tags(post_tags)

    else:
        raise Exception("undefined service type")

    # do some handling for different media element tag_types
    post['video'] = True if (post.get('file').endswith('webm') or post.get('file').endswith('mp4')) else False

    return render_template('post.html',
                            post=post,
                            tags=tags,
                            stats=stats,
                            post_tags=serialized_tags,
                            service=service,
                            archived=archived
                            )

def startup():
    '''Handle any application startup tasks'''
    import os
    if not os.path.isfile('postdata.db'):
        import create_data

if __name__ == "__main__":
    # handle any startup tasks
    startup()

    # run our scraper in another process
    scraper_process = Process(target=scraper_run)
    scraper_process.start()
    app.run()

    # join scraper after we finish
    scraper_process.join()
