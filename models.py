#from main import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import json

from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# TODO:
# add a source_url to tag / link where we got this from
# add a second table of post activity, how many times we have viewed
# a given post that we can use for analytics

Base = declarative_base()

engine = create_engine('sqlite:///postdata.db')


class Posts(Base):
    __tablename__ = 'posts'

    filename = Column(String, primary_key=True)
    id = Column(Integer)
    source = Column(String)
    score = Column(Integer)
    tags = Column(String)
    rating = Column(String)
    created_at = Column(String)
    status = Column(String)
    creator_id = Column(Integer)
    change = Column(Integer)

    @staticmethod
    def from_tuple(data):
        '''
        Enables initializing from a tuple to support raw
        queries.
        '''
        return Posts(
            filename=data[0],
            id=data[1],
            source=data[2],
            score=data[3],
            tags=data[4],
            rating=data[5],
            created_at=data[6],
            status=data[7],
            creator_id=data[8],
            change=data[9]
        )

    def get_filepath(self, filename):
        '''
        Return full static filepath for filename using
        our two depth hash prefix scheme.
        '''
        if filename:
            return 'static/dump/{}/{}/{}'.format(filename[:2], filename[2:4], filename)
        else:
            return None

    def as_dict(self):
        '''
        Returns posts instance as a json object
        '''
        data = {'filename':self.filename, 'id':self.id, 'source':self.source, 'score':self.score,
            'tags':self.tags.split('|'),
            'rating':self.rating, 'created_at':self.created_at,
            'status':self.status, 'creator_id':self.creator_id, 'change':self.change,
            'file':self.get_filepath(self.filename)
            }

        return data

class PostStat(Base):
    __tablename__ = 'post_stats'

    post_filename = Column(String, primary_key=True)
    post_id = Column(Integer)
    views = Column(Integer, default=0)
    rating = Column(Integer, default=0)

    def as_dict(self):
        '''
        returns poststat instance as json object
        '''
        return {'post_filename':self.post_filename, 'post_id':self.post_id, 'views':self.views, 'rating':self.rating}

class TagStat(Base):
    __tablename__ = 'tag_stats'

    tag = Column(String, primary_key=True)
    views = Column(Integer, default=0)
    searches = Column(Integer, default=0)

    def as_dict(self):
        '''
        returns tagstat instance as json object
        '''
        return {'tag':self.tag, 'views':self.views, 'searches':self.searches}

class Tag(Base):
    __tablename__ = 'tag'

    tag = Column(String, primary_key=True)
    count = Column(Integer)
    type = Column(String)
    ambiguous = Column(Integer)
    source = Column(String)

    def as_dict(self):
        '''
        Returns tag instance as a json object
        '''
        data = {'tag':self.tag, 'count':self.count, 'type':self.type, 'ambiguous':self.ambiguous,
            'source':self.source
            }

        return data

    @classmethod
    def serialize_tags(cls, tags=None, increment_views=False):
        serialized_tags = {'artist':[], 'character':[], 'copyright':[], 'tag':[]}
        tags = cls.get_tags(tags, increment_views)

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
    def get_tags(cls, tags=None, increment_views=False):
        '''
        Grab tag data from the local db
        '''
        local_tags = []
        for tag in tags:
            local_tag = session.query(cls).filter(cls.tag == tag).first()
            session.flush()
            if local_tag:
                local_tags.append(local_tag.as_dict())
                # increment views for each local tag we grabbed
                if increment_views:
                    print("debug tag stat")
                    print(tag)
                    tag_stat = session.query(TagStat).filter(TagStat.tag == tag).first()
                    tag_stat.views += 1
        session.commit()

        return local_tags


#Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = scoped_session(Session)
