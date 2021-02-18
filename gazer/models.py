#from main import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import json

from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

engine = create_engine('sqlite:///postdata.db')


class Posts(Base):
    __tablename__ = 'posts'

    filename = Column(String, primary_key=True)
    id = Column(Integer)
    booru = Column(String)
    source = Column(String)
    score = Column(Integer)
    tags = Column(String)
    dd_tags = Column(String)
    rating = Column(String)
    created_at = Column(String)
    status = Column(String)
    creator_id = Column(Integer)
    change = Column(Integer)
    views = Column(Integer, default=0)

    @staticmethod
    def from_tuple(data):
        '''
        Enables initializing from a tuple to support raw
        queries.
        '''
        return Posts(
            filename=data[0],
            id=data[1],
            booru=data[2],
            source=data[3],
            score=data[4],
            tags=data[5],
            rating=data[6],
            created_at=data[7],
            status=data[8],
            creator_id=data[9],
            change=data[10],
            views=data[11],
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
        data = {'filename':self.filename, 'id':self.id,
            'booru':self.booru,
            'source':self.source,
            'score':self.score,
            'tags':self.tags.split('|'),
            'dd_tags': self.dd_tags.split('|') if self.dd_tags else None,
            'rating':self.rating, 'created_at':self.created_at,
            'status':self.status, 'creator_id':self.creator_id,
            'change':self.change,
            'file':self.get_filepath(self.filename),
            'views':self.views,
            }

        return data


class Tag(Base):
    __tablename__ = 'tag'

    tag = Column(String, primary_key=True)
    count = Column(Integer)
    type = Column(String)
    ambiguous = Column(Integer)
    source = Column(String)
    views = Column(Integer, default=0)

    def as_dict(self):
        '''
        Returns tag instance as a json object
        '''
        data = {'tag':self.tag, 'count':self.count, 'type':self.type, 'ambiguous':self.ambiguous,
            'source':self.source, 'views':self.views
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
                # increment views for each local tag we grabbed
                if increment_views:
                    local_tag.views += 1
                local_tags.append(local_tag.as_dict())
            # tag isn't in db happens for dd derived tags
            else:
                local_tags.append({'tag':tag})
        session.commit()

        return local_tags


#Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = scoped_session(Session)
