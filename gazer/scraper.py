import time, json, os
from sources.gelbooru import gelbooru_api
from sources.konachan import konachan_api
from sources.lolibooru import lolibooru_api
from sources.yandere import yandere_api
from sources.safebooru import safebooru_api

from models import Posts, Tag, Base
from models import session

status_data = {"active":True, "current_tags":None, "images_downloaded": 0, "finished":False}
source_map = {gelbooru_api.source:gelbooru_api,
            konachan_api.source:konachan_api,
            lolibooru_api.source:lolibooru_api,
            yandere_api.source:yandere_api,
            safebooru_api.source:safebooru_api
            }

def scraper_run():
    '''Runs our scraper until we get through all listed tags'''
    if os.path.exists("gazer/scraper_data/lock"):
        return

    # process lock
    with open("gazer/scraper_data/lock", "w") as lock:
        pass

    with open("gazer/scraper_data/tag_set.json") as tags:
        tag_sets = json.load(tags)
    with open("gazer/scraper_data/config.json") as config:
        CONFIG = json.load(config)
    with open("gazer/scraper_data/status.json", "w") as status:
        json.dump(status_data, status)

    for tag_set in tag_sets:
        page = 0
        status_data["current_tags"] = tag_set["name"]
        with open("gazer/scraper_data/status.json", "w") as status:
            json.dump(status_data, status)

        while 1:
            #posts = gelbooru_api.get_posts(tags=tag_set["tags"], page=page)
            source_api = source_map[tag_set['source']]
            posts = source_api.get_posts(tags=tag_set["tags"], page=page)
            page += 1
            if not len(posts):
                break

            for post in posts:
                local_post = session.query(Posts.filename).filter(Posts.filename == post['image']).first()
                if not local_post:
                     new_post = source_api.get_post(post['id'])
                     post_tags = source_api.get_tags(new_post.get('tags'))
                     post_id = source_api.archive(new_post)
                     source_api.save_tags(post_tags)

                     status_data["images_downloaded"] += 1
                     with open("gazer/scraper_data/status.json", "w") as status:
                         json.dump(status_data, status)

                     time.sleep(CONFIG['delay'])

    status_data["finished"] = True
    with open("gazer/scraper_data/status.json", "w") as status:
        json.dump(status_data, status)

    # end process lock
    os.remove("gazer/scraper_data/lock")

    
