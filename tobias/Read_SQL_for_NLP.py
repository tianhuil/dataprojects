import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgresql:///arXivdata')
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
abstractclass = Table("abstractclass", metadata, 
                      Column('arxivid', String, primary_key = True),
                      Column('title', String),
                      Column('abstract', String),
                      Column('categories', String),
                      Column('msc_class', String),
                      extend_existing = True)
for paper in session.query(abstractclass).filter(abstractclass.c.arxivid == '0704.0005'):
    print paper.categories, paper.msc_class
