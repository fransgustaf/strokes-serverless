import json
import boto3
import base64

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), './../', 'shared_files'))
sys.path.append('/opt')
import django_setup
from django.db import models
from strokes.models import *

def lambda_handler(event, context):
	print('got event{}'.format(json.dumps(event)))

	if event['resource'].endswith('background'):
		handleBackground(event)

	else:
		if event['httpMethod'] == "POST" or event['httpMethod'] == "PUT":
			document = save_document(event)

			client = boto3.client('lambda', "ap-southeast-1")
			arguments = json.dumps({"body": json.dumps({"documentId": document.id})})

			print(arguments)
			client.invoke_async(
				FunctionName="RecogniserFunction",
				InvokeArgs= arguments
			)
			return {
				"isBase64Encoded": False,
				"statusCode": 200,
				"headers": {},
				"body": json.dumps({"id": document.id})
			}
		elif event['httpMethod'] == "GET":
			document_list = []
			for document in Document.objects.all():
				document_list.append({"id": document.id, "name": 	document.name})
			return {
				"isBase64Encoded": False,
				"statusCode": 200,
				"headers": {},
				"body": json.dumps(document_list)
			}

	return {
		"isBase64Encoded": False,
		"statusCode": 200,
		"headers": {},
		"body": ""
		}

def handleBackground(event):
	# "path": "/page/4874352/background"
	# "pathParameters": { "address": "4874352" }
	# "path": "/document/30/page/1/background"
	# "pathParameters": { "identifier": "30", "page_number": "1" }

	params = event['pathParameters']
	page_address = ''
	if 'identifier' in params:
		document = Document.objects.get(identifier=params['identifier'])
		pages = document.page_set
		for x in range(1, pages.count()):
		    print(x)
		    # ToDo fix when number is implemented
			#page = pages.filter(number=params['number'])
			#page_address = page.number
	else:
		address = params['address']

	print(address)
	json.dumps(event['body'])
	s3 = boto3.resource('s3')
	object = s3.Object('fs-background-images', '{0}.{1}'.format(address, "jpeg" if event['headers']['Content-Type'] else 'png'))
	object.put(Body=base64.decodestring(event['body']), ContentType='image/jpeg',ACL='public-read')


def save_document(event):
	params = event['pathParameters']
	params = event['pathParameters']

	identifier = None
	if 'identifier' in params:
		identifier = params['identifier']

	input_document = json.loads(event['body'])

	document = None
	document_setting = None
	if identifier:
		documents = Document.objects.filter(identifier=identifier)
		if documents.exists():
			document = documents.first()
			document_setting = DocumentSetting.objects.get(id=document.document_setting_id)
		else:
			new_document = False
			document_setting_id = input_document['documentSettingId']
			document_setting = DocumentSetting.objects.get(id=document_setting_id)
			document = Document(document_setting_id=document_setting.id, name=document_setting.default_name, identifier=identifier)
			document.save()

	for input_page in input_document['pages']:
		page_address = None
		if 'address' in input_page:
			page_address = input_page['address']
		page_number = None
		if 'number' in input_page:
			page_number = input_page['number']


		page = document.page_set.filter(address=page_address)
		page_setting = None
		if page.exists():
			page = document.page_set.filter(address=page_address).first()
			page_setting = PageSetting.objects.get(id=page.page_setting_id)
		else:	
			if page_number is not None:
				page_setting = PageSetting.objects.get(number=page_number)
			else:
				page_setting = PageSetting.objects.get(number=1)
			import uuid
			page = Page(page_setting_id=page_setting.id, document_id=document.id, address=uuid.uuid4() if page_address is None else page_address, number= 1 if page_number is None else page_number)
			page.save()

		# Create fields
		for field_setting in FieldSetting.objects.filter(page_setting_id=page_setting.id):
			field = Field(page_id=page.id, field_setting_id=field_setting.id)
			field.save()

		# Create strokes
		for input_stroke in input_page['strokes']:
			stroke = Stroke(page_id=page.id)
			stroke.save()
			dots_to_insert = []
			for input_dot in input_stroke['dots']:
				dots_to_insert.append(Dot(stroke_id=stroke.id, x=input_dot['x'], y=input_dot['y']))

			Dot.objects.bulk_create(dots_to_insert)

	return document

