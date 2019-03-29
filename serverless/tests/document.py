import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared_files'))
import database
from page import *

class Document:

	name = None
	pages = []
	document_id = None

	def __init__(self, name, pages):
		self.name = name
		self.pages = pages

	@staticmethod
	def load(document_id):
		document_id = document_id
		db = database.Database()

		pages = []
		for page_id in Page.get_document_page_ids(document_id):
			page = Page.load(page_id)
			pages.append(page)

		query = "SELECT * FROM strokes_document WHERE id IN ({0})".format(document_id)
		result = db.query(query, True)

		name = None
		for document in result:
			name = document.name

		return Document(name, pages)

	def get_myscript_format():
		return ""

	def save(self):
		db = database.Database()

		#Document
		query = "INSERT INTO strokes_document (name) VALUES ('{0}')".format(self.name)
		result = db.query(query)

		document_db_id = db.lastrowid()

		# Pages
		for page in self.pages:
			query = "INSERT INTO strokes_page (document_id, page_address) VALUES ('{0}', '{1}')".format(document_db_id, page.page_address)
			result = db.query(query)

			page_db_id = db.lastrowid()

			# Strokes
			for stroke in page.strokes:
				query = "INSERT INTO strokes_stroke (page_id) VALUES ('{0}')".format(page_db_id)
				result = db.query(query)
				
				stroke_db_id = db.lastrowid();

				# Dots
				query = "INSERT INTO strokes_dot (stroke_id, x, y) VALUES "
				query_values = []
				for dot in stroke.dots:
					query_values.append("('{0}', '{1}', '{2}')".format(stroke_db_id, dot.x, dot.y))
				query += str.join(',', query_values) 
				result = db.query(query)


#		conn.execute("SELECT * FROM strokes_document")


