from models import *

class Database:

	conn = None # Todo remove
	cursor = None # Todo remove

	_instance = None # Static variable

	def __init__(self):
		engine = create_engine('mysql+mysqlconnector://root:heyheyhey@strokes.cgf0r7uvrbjf.ap-southeast-1.rds.amazonaws.com/strokes') # Todo remove
		self.conn = engine.connect() # Todo remove

	@staticmethod
	def getInstance():
		if Database._instance is None:
			engine = create_engine('mysql+mysqlconnector://root:heyheyhey@strokes.cgf0r7uvrbjf.ap-southeast-1.rds.amazonaws.com/strokes')
			session = sessionmaker()
			session.configure(bind=engine)
			Base.metadata.create_all(engine)
			Database._instance = session()
		return Database._instance


	def query(self, query, return_result=False):
		print(query)
		self.cursor = self.conn.execute(query)

		#print(type(list(self.cursor)))

		if return_result == True:
			print("Returning list")
			return self.cursor.fetchall()

		return self.cursor

	def query_ids(self, query, not_used=True):
		print(query)
		self.cursor = self.conn.execute(query)

		ids = []
		for row in self.cursor.fetchall():
			ids.append(row['id'])

		return ids

	def lastrowid(self):
		return self.cursor.lastrowid


