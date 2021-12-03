from sqlalchemy import desc
from utilities import escapeString

from sources.gelbooru import gelbooru_api
from sources.yandere import yandere_api
from sources.konachan import konachan_api
from sources.lolibooru import lolibooru_api
from sources.safebooru import safebooru_api

from models import session
from models import Posts, Tag, Base

def tagSearch(tags, limit=None, page=None, service=None, sort=None, dd_enabled=False):
    '''
    Search for a list of tags in database using string LIKE method
    relies on pipe delimited tag list and string search. Not as optimized
    as I would like but linear worst case so maybe ok for our small
    local server.
    '''

    if service == 'archive':
        if not tags:
            if sort == "created-desc":
                results = session.query(Posts).order_by(desc('created_at')).limit(limit).offset(limit*page).all()
            elif sort == "created-asc":
                results = session.query(Posts).order_by('created_at').limit(limit).offset(limit*page).all()
            elif sort == "score-desc":
                results = session.query(Posts).order_by(desc('score')).limit(limit).offset(limit*page).all()
            elif sort == "score-asc":
                results = session.query(Posts).order_by('score').limit(limit).offset(limit*page).all()
            elif sort == "views-desc":
                results = session.query(Posts).order_by(desc('views')).limit(limit).offset(limit*page).all()
            elif sort == "views-asc":
                results = session.query(Posts).order_by('views').limit(limit).offset(limit*page).all()
            else:
                results = session.query(Posts).order_by(desc('id')).limit(limit).offset(limit*page).all()
            return [post.as_dict() for post in results]
        
        else:
            tag_query = ''
            tag_field = 'dd_tags' if dd_enabled else 'tags'
            order_clause = ''

            # giant if clause for ordering fix later
            if sort == "created-desc":
                order_clause = "ORDER BY created_at desc"
            elif sort == "created-asc":
                order_clause = "ORDER BY created_at"
            elif sort == "score-desc":
                order_clause = "ORDER BY score desc"
            elif sort == "score-asc":
                order_clause = "ORDER BY score asc"
            elif sort == "views-desc":
                order_clause = "ORDER BY views desc"
            elif sort == "views-asc":
                order_clause = "ORDER BY views"

            for i, tag in enumerate(tags):
                tag_escaped = escapeString(tag)
                if i == 0:
                    tag_query += '''{} LIKE '%|{}|%' '''.format(tag_field, tag_escaped)
                else:
                    tag_query += '''AND {} LIKE '%|{}|%' '''.format(tag_field, tag_escaped)

            query = '''SELECT * FROM posts
                        WHERE {}
                        {}
                        LIMIT {} OFFSET {}
                        '''.format(tag_query, order_clause, limit, limit*page)
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