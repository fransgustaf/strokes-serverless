import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared_files'))

import django_setup
from django.db import models
from strokes.models import *

document = Document.objects.get(id=4)
print (document.name)

for page in document.page_set.all():
    strokes_data = []
    for stroke in page.stroke_set.all():
        x = []
        y = []
        for dot in stroke.dot_set.all():
            x.append(float(dot.x))
            y.append(float(dot.y))
                     
        strokes_data.append({"type": "stroke", "x": x, "y": y})

myscript_json = { "textParameter": { "language": "en_US", "textInputMode": "CURSIVE" }, "inputUnits": [ {  "textInputType": "MULTI_LINE_TEXT",  "components": strokes_data }]}

print (myscript_json)


quit()

page = Page.objects.get(id=document.id)
print (page.id)
stroke = Stroke.objects.Page.first()
print (stroke.id)
dots= stroke.objects.Dot.first()
print (dot.id)
