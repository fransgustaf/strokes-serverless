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
	run_recognitions(document_id)


#	response = requests.request("POST", "http://google.com")
#	if response.text == "":
#		response.text = {"result":{"textSegmentResult":{"selectedCandidateIdx":0,"candidates":[{"label":"BEER","normalizedScore":1.0,"resemblanceScore":0.56634593,"children": None}]}},"instanceId":"13804477-eea4-4e2a-a290-dc4098fb0e1a"}


	## {"result":{"textSegmentResult":{"selectedCandidateIdx":0,"candidates":[{"label":"BEER","normalizedScore":1.0,"resemblanceScore":0.56634593,"children":null}]}},"instanceId":"13804477-eea4-4e2a-a290-dc4098fb0e1a"}

	return {
	'statusCode': 200,
	'body': "thumbs up"
	}


def run_recognitions(document_id):

	document = Document.objects.get(id=document_id)

	for page in document.page_set.all():
		for field in page.field_set.all():
			field_setting = FieldSetting.objects.get(id=field.field_setting_id)
			recognition_settings = RecognitionSetting.objects.filter(field_setting_id=field_setting.id)
			# Set recognition settings from recogntion settings
			if recognition_settings.exists():
				recognition_setting = recognition_settings.first()
				myscript_json = get_myscript_json(page.stroke_set.all(), field, field_setting, recognition_setting)
				response = run_recognition(myscript_json)
				print(response.text)
		
				save_recognition_result(field.id, response.text)



def get_myscript_json(stroke_set, field, field_setting, recognition_setting):
	strokes_data = []
	print("Field setting x: {0}, y: {1}, width: {2}, heigth: {3}").format(field_setting.x, field_setting.y, field_setting.width, field_setting.height)
	for stroke in stroke_set.all():
		x = []
		y = []
		for dot in stroke.dot_set.all():
			#print("Dot x: {0}, y: {1},").format(dot.x, dot.y)
			good_stroke = False
			x.append(float(dot.x))
			y.append(float(dot.y))
			# Field setting x: 0.000000, y: 297.000000, width: 210.000000, heigth: 130.000000
			# Dot x: 86.333333, y: 196.666667,
			if dot.x > field_setting.x and dot.x < field_setting.x+field_setting.width and dot.y < field_setting.y and dot.y > field_setting.y-field_setting.height:
				good_stroke = True
		
		if good_stroke:
			strokes_data.append({"type": "stroke", "x": x, "y": y})

	myscript_json = json.dumps({ "textParameter": { "language": "{0}".format(recognition_setting.language), "textInputMode": "{0}".format(recognition_setting.input_mode) }, "inputUnits": [ {  "textInputType": "{0}".format(recognition_setting.input_type),  "components": strokes_data }]})
	return myscript_json

def run_recognition(strokes):
	headers = {
	'content-type': ("multipart/form-data; boundary={0}").format(boundary),
	'Content-Type': "application/javascript",
	'Cache-Control': "no-cache",
	}

	payload = create_multipart(boundary, strokes)

	return requests.request("POST", myscript_url, data = payload, headers = headers)


# {"result":{"textSegmentResult":{"selectedCandidateIdx":0,"candidates":[{"label":"i. It.","normalizedScore":1.0,"resemblanceScore":0.5168961,"children":null}]}},"instanceId":"296cbe8b-3018-4b6b-bec0-a44b63a8fe7d"}
def save_recognition_result(field_id, result):
	result_json = json.loads(result)

	if 'textSegmentResult' in result_json['result']:
		RecognitionResult.objects.filter(field_id=field_id).delete()
		recognition_result = RecognitionResult(field_id=field_id, selected_candidate_id=int(result_json['result']['textSegmentResult']['selectedCandidateIdx']))
		recognition_result.save()

		for candidate in result_json['result']['textSegmentResult']['candidates']:
			recognition_candidate = RecognitionCandidate(recognition_result_id=recognition_result.id, value=candidate['label'], normalized_score=candidate['normalizedScore'], resemblance_score=candidate['resemblanceScore'])
			recognition_candidate.save()


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
