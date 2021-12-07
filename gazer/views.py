from flask import Flask, render_template, request, abort
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import json
import requests
import shutil
import os
from multiprocessing import Process
from gazer.scraper import scraper_run
from gazer.utilities import escapeString

from gazer.sources.gelbooru import gelbooru_api
from gazer.sources.yandere import yandere_api
from gazer.sources.konachan import konachan_api
from gazer.sources.lolibooru import lolibooru_api
from gazer.sources.safebooru import safebooru_api

from gazer.search import tagSearch

from gazer.models import session
from gazer.models import Posts, Tag, Base
from gazer import app

@app.route('/')
def index():
    '''
    Main page display index and navigation menu 
    '''
    return render_template('index.html')

@app.route('/tags')
def tags():
    ''' 
    Display basic list of most viewed tags
    '''
    tags = session.query(Tag).order_by(desc(Tag.views)).limit(100).all()
    tags = [tag.as_dict() for tag in tags]
    return render_template("tags.html", tags=tags)

@app.route('/tag/<name>')
def tag(name):
    ''' 
    Display information about a particular tag
    ''' 
    tag = session.query(Tag).filter(Tag.tag==name).first()
    if tag:
        return json.dumps(tag.as_dict())
    else:
        abort(404)

@app.route('/tagcomplete/<field>')
def tagcomplete(field):
    '''
    Return closest tags for typed text
    '''
    input_tags = field.split(' ')
    last_tag = input_tags[-1]

    search = "{}%".format(last_tag)
    tags = session.query(Tag).filter(Tag.tag.like(search)) \
        .order_by(Tag.count.desc()) \
        .limit(10).all()

    tags = [tag.as_dict() for tag in tags]
    output = []
    for tag in tags:
        tag_name = ' '.join(input_tags[:-1]) + ' ' + tag.get("tag")
        output.append(tag_name)
        
    return json.dumps(output)

@app.route('/poststats')
def poststats():
    '''
    Display information about the most viewed posts 
    '''
    posts = session.query(Posts).order_by(desc(Posts.views)).limit(100).all()
    posts = [stat.as_dict() for stat in posts]
    return render_template("poststats.html", posts=posts)

@app.route('/scraper', methods = ["GET", "POST"])
def scraper():
    '''
    Display interface for booru scraper 
    '''
    if request.method == "POST":
        scraper_process = Process(target=scraper_run)
        scraper_process.start()

    with open("gazer/scraper_data/tag_set.json") as tags:
        tag_set = json.load(tags)
    with open("gazer/scraper_data/status.json") as status:
        current_status = json.load(status)

    return render_template("scraper.html", tag_set=tag_set, status=current_status)


@app.route('/posts')
def posts():
    '''
    Display main posts page for archive/booru client 
    '''
    page = int(request.args.get('page', 0))
    limit = int(request.args.get('limit', 25))
    thumb_size = int(request.args.get('thumb_size', 200))
    service = request.args.get('service', 'archive')
    sort = request.args.get('sort', 'created-desc')
    dd_enabled = True if request.args.get('dd_enabled') else False
    tags = request.args.get('tags', '')

    search_tags = tags.split()
    posts = tagSearch(search_tags, page=page, limit=limit, service=service, sort=sort, dd_enabled=dd_enabled)

    # handle local webm and mp4s
    for post in posts:
        local_vid = True if (post.get('file') and (post.get('file').endswith('webm') or post.get('file').endswith('mp4'))) else False
        booru_vid = True if (post.get('file_url') and (post.get('file_url').endswith('webm') or post.get('file_url').endswith('mp4'))) else False
        post['video'] = local_vid or booru_vid

    # easy way to handle our state is just to pass back the
    # values that the page was called with for use in our relative links
    return render_template('posts.html',
                            title='post test',
                            service=service,
                            tags=tags,
                            posts=posts,
                            page=page,
                            limit=limit,
                            sort=sort,
                            dd_enabled=dd_enabled,
                            thumb_size=thumb_size,
                            )

# this needs some sort of cleanup getting messy
@app.route('/post/<int:id>')
def post(id):
    '''
    Display an individual post 
    '''
    service = request.args.get('service', 'archive')
    tags = request.args.get('tags', '')
    archived = False
    post_tags = []
    serialized_dd_extra_tags = None
    limit = int(request.args.get('limit', 25))
    thumb_size = int(request.args.get('thumb_size', 200))
    sort = request.args.get('sort', 'created-desc')
    dd_enabled = True if request.args.get('dd_enabled') else False

    search_tags = tags.split()

    stats = None
    if service == 'archive':
        archived = True
        post = session.query(Posts).filter(Posts.id==id).first()
        post.views += 1
        session.commit()
        post = post.as_dict()
        serialized_tags = Tag.serialize_tags(post.get('tags'), increment_views=True)

        if post.get('dd_tags'):
            dd_extra_tags = list(set(post.get('dd_tags')) - set(post.get('tags')))
            serialized_dd_extra_tags = Tag.serialize_tags(dd_extra_tags)

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
                            dd_tags=serialized_dd_extra_tags,
                            service=service,
                            limit=limit,
                            dd_enabled=dd_enabled,
                            thumb_size=thumb_size,
                            sort=sort,
                            archived=archived
                            )