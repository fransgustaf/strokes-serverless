from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
Base = declarative_base()

class Document(Base):
    __tablename__ = 'strokes_document'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))

 
from sqlalchemy import create_engine
engine = create_engine('mysql+mysqlconnector://root:heyheyhey@strokes.cgf0r7uvrbjf.ap-southeast-1.rds.amazonaws.com/strokes')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s = session()

print s.query(Document).get(39).id


