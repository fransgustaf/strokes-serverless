import requests
import json
from sqlalchemy import create_engine

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared_files'))

import django_setup
from django.db import models
from strokes.models import *

boundary = "XXXXXXXXXXXXX"
url = "https://cloud.myscript.com/api/v3.0/recognition/rest/text/doSimpleRecognition.json"
application_key = "4443cea5-ada7-4d9f-be9b-6d68f530d2e1"

# Multi part only works in Python 2.7 for some reason. Take care of when rerdoing multipart section properly.

def lambda_handler(event, context):

	#strokes = Document.objects.get(id=39).Page.objects.first().
	#doc = Document.load(39)
	#print(doc.pages)
	#strokes = Stroke.get_myscript_format(doc.pages[0].strokes)
	#strokes = '{ "textParameter": { "language": "en_US", "textInputMode": "CURSIVE" }, "inputUnits": [ {  "textInputType": "MULTI_LINE_TEXT",  "components": [ { "type": "stroke", "x": [ 170, 169, 161, 154, 147, 142, 137, 133, 131, 128, 126, 123, 121, 120, 119, 119, 119, 119, 119, 119, 119, 119, 119, 120, 120, 121, 122, 122, 123, 123, 124, 127, 129, 132, 136, 140, 144, 150, 154, 158, 163, 165, 168, 171, 173, 174, 175, 175, 175, 173, 169, 166, 163, 161, 160, 158, 157, 156, 156, 156, 156, 155, 155, 154, 153, 152, 152, 152, 151, 151, 151, 150, 148, 147, 147, 146 ], "y": [ 146, 146, 146, 146, 146, 146, 146, 146, 147, 151, 154, 159, 162, 165, 167, 169, 170, 172, 176, 181, 189, 194, 198, 202, 205, 208, 210, 211, 212, 213, 213, 214, 215, 216, 218, 219, 219, 219, 218, 217, 214, 212, 209, 205, 203, 201, 200, 199, 197, 195, 192, 189, 188, 186, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185, 185 ] }, { "type": "stroke", "x": [ 197, 197, 197, 197, 197, 197, 197, 197, 197, 197, 198, 198, 199, 200, 200, 201, 202, 203, 204, 206, 207, 209, 211, 212, 215, 218, 221, 223, 226, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 238, 238, 238, 238, 238, 238, 238, 238, 238, 238, 238, 238, 238, 237, 237 ], "y": [ 145, 149, 156, 164, 170, 177, 182, 190, 193, 196, 198, 200, 201, 202, 203, 203, 205, 206, 208, 210, 212, 213, 214, 214, 214, 214, 214, 214, 213, 212, 211, 209, 208, 206, 203, 198, 193, 185, 170, 161, 151, 144, 138, 134, 132, 131, 130, 130, 134, 140, 142, 144, 144, 145, 145 ] }, { "type": "stroke", "x": [ 283, 282, 281, 280, 278, 274, 272, 268, 266, 264, 264, 264, 264, 264, 264, 262, 262, 262, 262, 262, 262, 263, 268, 274, 280, 284, 288, 290, 291, 293, 293, 294, 295, 297, 298, 299, 299, 299, 299, 299, 298, 296, 293, 289, 285, 283, 280, 276, 272, 269, 268, 267, 267, 267, 267, 267 ], "y": [ 143, 143, 143, 143, 143, 147, 149, 152, 154, 155, 156, 156, 157, 159, 162, 168, 171, 174, 175, 176, 176, 178, 179, 180, 181, 182, 183, 183, 183, 184, 186, 189, 194, 199, 202, 205, 206, 207, 207, 208, 208, 209, 210, 211, 213, 213, 213, 213, 213, 212, 211, 211, 211, 211, 210, 210 ] }  ] } ]}'


	run_recognitions(4)


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

	# Todo multiple pages
	page = document.page_set.first()

	for field in page.field_set.all():
		field_setting = FieldSetting.objects.get(id=field.field_setting_id)
		recognition_setting = RecognitionSetting.objects.get(field_setting_id=field_setting.id)
		# Set recognition settings from recogntion settings
		myscript_json = get_myscript_json(page.stroke_set.all(), field, field_setting)
		response = run_recognition(myscript_json)
		print(response.text)
	
		save_recognition(field.id, recognition_setting.id, response.text)



def get_myscript_json(stroke_set, field, field_setting):
	strokes_data = []
	for stroke in stroke_set.all():
		x = []
		y = []
		for dot in stroke.dot_set.all():
			good_stroke = False
			x.append(float(dot.x))
			y.append(float(dot.y))
			if dot.x > field_setting.x and dot.x < field_setting.x+field_setting.width and dot.y > field_setting.y and dot.y < field_setting.y+field_setting.height:
				good_stroke = True
		
		if good_stroke:
			strokes_data.append({"type": "stroke", "x": x, "y": y})

	myscript_json = json.dumps({ "textParameter": { "language": "en_US", "textInputMode": "CURSIVE" }, "inputUnits": [ {  "textInputType": "MULTI_LINE_TEXT",  "components": strokes_data }]})
	return myscript_json

def run_recognition(strokes):
	headers = {
	'content-type': ("multipart/form-data; boundary={0}").format(boundary),
	'Content-Type': "application/javascript",
	'Cache-Control': "no-cache",
	}

	payload = create_multipart(boundary, strokes)

	return requests.request("POST", url, data = payload, headers = headers)


# {"result":{"textSegmentResult":{"selectedCandidateIdx":0,"candidates":[{"label":"i. It.","normalizedScore":1.0,"resemblanceScore":0.5168961,"children":null}]}},"instanceId":"296cbe8b-3018-4b6b-bec0-a44b63a8fe7d"}
def save_recognition(field_id, recognition_setting_id, result):
	result_json = json.loads(result)

	recognition = Recognition(field_id=field_id, recognition_setting_id=recognition_setting_id, selected_candidate_id=int(result_json['result']['textSegmentResult']['selectedCandidateIdx']))
	recognition.save()

	for candidate in result_json['result']['textSegmentResult']['candidates']:
		recognition_candidate = RecognitionCandidate(recognition_id=recognition.id, value=candidate['label'], normalizedScore=candidate['normalizedScore'], resemblanceScore=candidate['resemblanceScore'])
		recognition_candidate.save()


def create_multipart(boundary, strokes):
	boundary_block = ("--{0}").format(boundary)
	new_line = "\r\n"

	application_key_block = ('Content-Disposition: form-data; name="applicationKey"{0}{1}{2}').format(new_line, new_line, application_key)
	#print(application_key_block)

	strokes_block = ('Content-Disposition: form-data; name="textInput"{0}{1}{2}').format(new_line, new_line, strokes)
	#print(strokes_block)

	payload = ("{0}{1}{2}{3}{4}{5}{6}{7}{8}").format(boundary_block, new_line, application_key_block, new_line, boundary_block, new_line, strokes_block, new_line, boundary_block)
	print(payload)
	return payload
