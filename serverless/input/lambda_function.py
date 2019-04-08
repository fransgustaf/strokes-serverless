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

	if event['resource'].endswith('background'):
		handleBackground(event)

	elif event['resource'] == "/documentSetting":
		document_setting_id = DocumentSetting.save_document_settings(event, customer.id)

		return {
			"isBase64Encoded": False,
			"statusCode": 200,
			"headers": {},
			"body": document_setting_id
		}

	else:
		if event['httpMethod'] == "POST" or event['httpMethod'] == "PUT":
			document = Document.save_document(event, customer.id)

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

	return {
		"isBase64Encoded": False,
		"statusCode": 200,
		"headers": {},
		"body": ""
		}

# ToDo put model logic in models.py to avoid customers affecting each others data
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


