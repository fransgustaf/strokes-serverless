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
	'content-type': ("multipart/form-data; boundary={0}").format(boundary)
	}

	payload = create_multipart(boundary, strokes)

	return requests.request("POST", myscript_url, data = payload, headers = headers)


def create_multipart(boundary, strokes):

	application_key_block = ('Content-Disposition: form-data; name="applicationKey"\r\n\r\n{0}').format(myscript_application_key)
	#print(application_key_block)

	strokes_block = ('Content-Disposition: form-data; name="textInput"\r\n\r\n{0}').format(strokes)
	#print(strokes_block)

	#payload = ('\r\n--XXXXXXXXXXXXX\r\nContent-Disposition: form-data; name="applicationKey"\r\n\r\n4443cea5-ada7-4d9f-be9b-6d68f530d2e1\r\n--XXXXXXXXXXXXX\r\nContent-Disposition: form-data; name="textInput"\r\n\r\n{"textParameter": {"language": "en_US", "textInputMode": "CURSIVE"}, "inputUnits": [{"textInputType": "MULTI_LINE_TEXT", "components": [{"type": "stroke", "x": [17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667, 17.666667], "y": [18.0, 18.666667, 20.0, 21.666667, 23.0, 34.0, 37.333333, 40.0, 42.333333, 43.333333, 50.333333, 51.666667, 52.0, 52.0, 52.333333]}, {"type": "stroke", "x": [18.0, 20.333333, 21.0, 23.0, 28.0, 29.0, 30.0, 30.333333, 30.333333, 31.666667, 31.666667, 31.666667, 31.333333, 31.0, 30.0, 29.666667, 28.666667, 27.0, 27.0, 25.0, 24.333333, 19.0, 19.0], "y": [18.666667, 18.666667, 18.666667, 18.666667, 18.666667, 18.666667, 18.666667, 19.0, 19.333333, 23.333333, 24.0, 26.0, 29.333333, 31.0, 31.666667, 32.333333, 33.0, 33.666667, 34.0, 34.333333, 34.333333, 34.333333, 34.333333]}, {"type": "stroke", "x": [51.666667, 50.333333, 49.0, 48.666667, 48.333333, 47.333333, 47.0, 46.666667, 46.333333, 44.666667, 43.0, 41.666667, 41.0, 40.0, 39.0, 39.0, 39.0, 39.0, 40.333333, 43.333333, 44.333333, 47.333333, 48.0, 48.0, 48.333333, 50.0, 50.333333, 50.666667, 50.666667, 50.666667, 50.666667, 50.666667, 50.666667, 50.666667, 50.666667, 50.666667, 51.333333, 51.666667, 51.666667, 52.0, 52.0], "y": [18.333333, 18.333333, 18.333333, 18.333333, 18.333333, 18.333333, 18.333333, 18.333333, 18.333333, 19.666667, 22.333333, 24.666667, 27.0, 30.0, 33.0, 33.666667, 33.666667, 34.0, 34.0, 31.0, 29.0, 24.0, 23.666667, 23.333333, 23.333333, 22.0, 21.666667, 21.666667, 21.666667, 21.333333, 21.333333, 20.666667, 20.666667, 20.333333, 20.333333, 24.333333, 27.666667, 29.0, 31.0, 32.666667, 33.0]}, {"type": "stroke", "x": [66.333333, 66.333333, 66.333333, 66.333333, 66.333333, 66.333333, 67.333333, 68.666667, 69.333333, 69.666667, 70.0, 70.0, 70.333333, 71.666667, 73.0, 74.0, 74.333333, 75.333333, 75.333333, 75.333333, 75.333333, 75.333333, 75.333333, 75.333333, 75.333333, 75.0, 74.666667, 72.0, 71.666667, 71.0, 70.666667, 69.333333, 69.0, 68.333333, 68.0, 67.0, 65.666667, 63.0, 60.0, 59.0, 58.666667, 58.666667, 58.333333, 57.666667, 57.666667, 57.0, 56.333333, 56.0, 56.0], "y": [18.666667, 21.333333, 23.333333, 25.333333, 26.0, 28.666667, 30.0, 31.0, 31.333333, 31.666667, 31.666667, 31.666667, 31.333333, 29.666667, 28.666667, 27.666667, 27.0, 21.666667, 21.333333, 20.666667, 20.333333, 19.666667, 17.333333, 17.0, 16.0, 17.333333, 19.0, 34.333333, 39.666667, 41.333333, 43.0, 47.0, 47.666667, 49.666667, 50.333333, 50.333333, 50.333333, 50.333333, 49.333333, 49.333333, 49.0, 49.0, 49.0, 47.666667, 47.333333, 45.333333, 44.0, 42.666667, 42.666667]}, {"type": "stroke", "x": [33.333333, 34.0, 41.333333, 44.333333, 45.666667], "y": [97.0, 97.0, 97.0, 97.0, 97.0]}, {"type": "stroke", "x": [54.666667, 54.666667, 54.666667, 54.666667, 54.666667, 54.666667, 54.666667, 54.666667, 55.0, 55.333333, 55.333333, 55.333333, 55.333333, 55.333333, 55.333333, 54.0, 54.0, 54.0, 54.0, 55.0, 56.666667, 57.666667, 58.0, 58.333333, 60.666667, 61.0, 61.333333, 62.0, 65.0, 66.333333, 67.333333, 68.0, 68.666667, 72.666667, 72.666667], "y": [96.666667, 100.333333, 101.666667, 105.0, 106.666667, 113.333333, 113.666667, 114.666667, 115.666667, 117.333333, 118.333333, 120.333333, 120.333333, 120.333333, 120.0, 116.333333, 113.333333, 112.666667, 110.0, 104.0, 102.0, 101.0, 100.333333, 99.333333, 96.0, 95.666667, 95.333333, 95.0, 94.666667, 94.666667, 95.0, 95.333333, 96.0, 99.0, 99.0]}, {"type": "stroke", "x": [87.333333, 87.0, 87.0, 87.0, 87.0, 87.0, 87.333333, 87.666667, 87.666667, 88.0, 89.0, 89.333333, 89.666667, 89.666667, 90.0, 90.666667, 90.666667, 90.666667, 90.666667, 90.666667, 89.333333, 89.0, 89.0, 89.0, 89.0], "y": [85.0, 85.0, 86.666667, 87.0, 87.333333, 87.333333, 88.333333, 88.666667, 89.0, 89.333333, 90.0, 90.0, 90.0, 90.0, 90.0, 89.666667, 89.333333, 89.0, 89.0, 87.666667, 85.333333, 85.333333, 85.333333, 85.333333, 85.333333]}]}]}\r\n--XXXXXXXXXXXXX')
	#payload = ('--{0}\r\nContent-Disposition: form-data; name="applicationKey"\r\n\r\n{1}\r\n--{2}\r\n{3}\r\n--{4}').format(boundary, myscript_application_key, boundary, strokes_block, boundary)
	
	payload = ('--{0}\r\n{1}\r\n--{2}\r\n{3}\r\n--{4}').format(boundary, application_key_block, boundary, strokes_block, boundary)
	print(payload)
	return payload
