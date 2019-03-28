from __future__ import print_function
import json
import boto3

import sys

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared_files'))
import django_setup
from django.db import models
from strokes.models import *

def lambda_handler(event, context):
	#client = boto3.client('lambda', "ap-southeast-1")
	#client.invoke_async(
	#	FunctionName="myscript",
	#	InvokeArgs=json.dumps(event)
	#)
	
	#print('got event{}'.format(json.dumps(event)))
	document = save_document(event)

	return {
		'document_id' : document_id
	}

def save_document(data):
	import datetime, time

	input_document = data

	document_setting_id = input_document['documentSettingId']

	# Assume document doesn't exist
	document_setting = DocumentSetting.objects.get(id=document_setting_id)
	document = Document(document_setting_id=document_setting.id, name=document_setting.default_name)
	document.save()

	# Todo multiple pages
	page_setting = PageSetting.objects.get(document_setting_id=document_setting_id)
	page = Page(page_setting_id=page_setting.id, document_id=document.id)
	page.save()

	# Create fields
	for field_setting in FieldSetting.objects.filter(page_setting_id=page_setting.id):
		field = Field(page_id=page.id, field_setting_id=field_setting.id)
		field.save()

	# Create strokes
	for input_stroke in input_document['data']:
		stroke = Stroke(page_id=page.id)
		stroke.save()
		dots_to_insert = []
		for input_dot in input_stroke['dots']:
			dots_to_insert.append(Dot(stroke_id=stroke.id, x=input_dot['x'], y=input_dot['y']))

		Dot.objects.bulk_create(dots_to_insert)

	return document

