import requests
import json

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), './../', 'shared_files'))
sys.path.append('/opt')
import django_setup
from django.db import models
from strokes.models import *

boundary = "XXXXXXXXXXXXX"
myscript_url = "https://cloud.myscript.com/api/v3.0/recognition/rest/text/doSimpleRecognition.json"
myscript_application_key = "4443cea5-ada7-4d9f-be9b-6d68f530d2e1"

# Multi part only works in Python 2.7 for some reason. Take care of when rerdoing multipart section properly.

def lambda_handler(event, context):
	print('got event{}'.format(json.dumps(event)))
	document_id = json.loads(event['body'])['documentId']

	customer = Customer.objects.get(api_key=event['requestContext']['identity']['apiKey'])

	run_recognitions(document_id, customer.id)

	## {"result":{"textSegmentResult":{"selectedCandidateIdx":0,"candidates":[{"label":"BEER","normalizedScore":1.0,"resemblanceScore":0.56634593,"children":null}]}},"instanceId":"13804477-eea4-4e2a-a290-dc4098fb0e1a"}

	return {
	'statusCode': 200,
	'body': "thumbs up"
	}


def run_recognitions(document_id, customer_id):
	document = Document.get_document(document_id, customer_id)

	for page in document.get_pages():
		for field in page.get_fields():
			field_setting = field.get_field_setting()

			recognition_setting = field_setting.get_recognition_setting()
			if(recognition_setting is not None):
				myscript_json = page.get_myscript_json(field, field_setting, recognition_setting)
				response = run_recognition(myscript_json)
				print(response.text)
		
				RecognitionResult.save_recognition_result(field.id, response.text, customer_id)


def run_recognition(strokes):
	headers = {
	'content-type': ("multipart/form-data; boundary={0}").format(boundary),
	'Content-Type': "application/javascript",
	'Cache-Control': "no-cache",
	}

	payload = create_multipart(boundary, strokes)

	return requests.request("POST", myscript_url, data = payload, headers = headers)


def create_multipart(boundary, strokes):
	boundary_block = ("--{0}").format(boundary)
	new_line = "\r\n"

	application_key_block = ('Content-Disposition: form-data; name="applicationKey"{0}{1}{2}').format(new_line, new_line, myscript_application_key)
	#print(application_key_block)

	strokes_block = ('Content-Disposition: form-data; name="textInput"{0}{1}{2}').format(new_line, new_line, strokes)
	#print(strokes_block)

	payload = ("{0}{1}{2}{3}{4}{5}{6}{7}{8}").format(boundary_block, new_line, application_key_block, new_line, boundary_block, new_line, strokes_block, new_line, boundary_block)
	print(payload)
	return payload
