from models import *
from recognition import Recognition
from fieldobj import FieldObj

import database

_field = FieldObj.load(1)
print _field._id
print _field.get_recognition()

quit()


 
from sqlalchemy import create_engine
engine = create_engine('mysql+mysqlconnector://root:heyheyhey@strokes.cgf0r7uvrbjf.ap-southeast-1.rds.amazonaws.com/strokes')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s = session()

print s.query(Document).first().id
print s.query(Page).first().id
print s.query(Field).first().id
print s.query(RecognitionResult).first().id
print s.query(RecognitionCandidate).first().id
print s.query(Stroke).first().id
print s.query(Dot).first().id


