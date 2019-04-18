import json
import boto3
import base64
import uuid

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), './../', 'shared_files'))
sys.path.append('/opt')
import django_setup
from django.db import models
from strokes.models import *

def lambda_handler(event, context):
	print('got event{}'.format(json.dumps(event)))
	customer = Customer.objects.get(api_key=event['requestContext']['identity']['apiKey'])
	event_body = json.loads(event['body'])
	params = event['pathParameters']
	# "resource": "/document/{identifier}",
	# "resource": "/document/{identifier}",
	# /document/{identifier}/page/{number}

	current_path = get_path(event['path'])

	if current_path =='background':
		handleBackground(event)

	elif current_path == "documentSetting":
		document_setting = DocumentSetting.save_document_setting(event_body, customer.id)

		return {
			"isBase64Encoded": False,
			"statusCode": 200,
			"headers": {},
			"body": document_setting.id
		}

	elif current_path == "document":
		if event['httpMethod'] == "POST" or event['httpMethod'] == "PUT":
			identifier = None
			if params and 'identifier' in params:
				identifier = params['identifier']

			input_document = json.loads(event['body'])
			document = Document.save_document(input_document, identifier, customer.id)

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
				document_list.append({"id": document.id, "name": document.name})
			return {
				"isBase64Encoded": False,
				"statusCode": 200,
				"headers": {},
				"body": json.dumps(document_list)
			}

	elif current_path == "page":
		page = Page.save_page(customer.id, event_body, params['address'], params['identifier'])

		return {
			"isBase64Encoded": False,
			"statusCode": 200,
			"headers": {},
			"body": page.address
		}

	elif current_path == "stroke":
		# /page/{address}/stroke
		# /document/{identifier}/page/{number}/stroke
		if event['httpMethod'] == "PUT":
			page_address = ''
			if 'address' in params:
				stroke = Stroke.save_by_address(params['address'], event_body, customer.id)
			else:
				stroke = Stroke.save_by_document_page(params['identifier'], params['number'], event_body, customer.id)

		return {
			"isBase64Encoded": False,
			"statusCode": 200,
			"headers": {},
			"body": stroke.id
		}

	return {
		"isBase64Encoded": False,
		"statusCode": 200,
		"headers": {},
		"body": ""
		}

# Get current path
def get_path(path):
	available_paths = ['documentSetting', 'pageSetting', 'fieldSetting', 'recognitionSetting', 'document', 'page', 'field', 'stroke', 'background']
	for available_path in available_paths:
		print("checking: {0} for: {1}".format(path, available_path))
		if path.endswith(available_path):
			print("found path: {0}".format(available_path))
			return available_path
	return get_path(path.rsplit('/',1)[0])

# ToDo put model logic in models.py to avoid customers affecting each others data
def handleBackground(event):
	# "path": "/page/4874352/background"
	# "paxthParameters": { "address": "4874352" }
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


