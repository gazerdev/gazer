import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///postdata.db')

from models import Posts, Base

Base.metadata.create_all(engine)

Session = sessionmaker(bind = engine)
session = Session()
