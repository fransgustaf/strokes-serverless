import uuid
from django.db import models

class DocumentSetting(models.Model):
    default_name = models.CharField(max_length=200, default="A new default document name")

class PageSetting(models.Model):
    document_setting = models.ForeignKey(DocumentSetting, on_delete=models.CASCADE)
    number = models.IntegerField(null=False)
    width = models.DecimalField(max_digits=20, decimal_places=6)
    height = models.DecimalField(max_digits=20, decimal_places=6)

class FieldSetting(models.Model):
    page_setting = models.ForeignKey(PageSetting, on_delete=models.CASCADE)
    x = models.DecimalField(max_digits=20, decimal_places=6)
    y = models.DecimalField(max_digits=20, decimal_places=6)
    width = models.DecimalField(max_digits=20, decimal_places=6)
    height = models.DecimalField(max_digits=20, decimal_places=6)

class RecognitionSetting(models.Model):
    field_setting = models.ForeignKey(FieldSetting, on_delete=models.CASCADE)
    input_mode = models.CharField(max_length=20, default="CURSIVE")
    input_type = models.CharField(max_length=20, default="MULTI_LINE_TEXT")
    language = models.CharField(max_length=20, default="en_US")
    
class Document(models.Model):
    name = models.CharField(max_length=200)
    identifier = models.CharField(max_length=50, default=uuid.uuid4)
    document_setting = models.ForeignKey(DocumentSetting, on_delete=models.CASCADE)

class Page(models.Model):
    page_setting = models.ForeignKey(PageSetting, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, default=uuid.uuid4)
    number = models.IntegerField(null=False)
    
class Field(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    field_setting = models.ForeignKey(FieldSetting, on_delete=models.CASCADE)
    recognition_setting = models.ForeignKey(RecognitionSetting, on_delete=models.CASCADE, null=True)

class RecognitionResult(models.Model):
    field = models.OneToOneField(Field, on_delete=models.CASCADE, primary_key=True,)
    selected_candidate_id = models.IntegerField(null=True)

class RecognitionCandidate(models.Model):
    recognition_result = models.ForeignKey(RecognitionResult, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    normalized_score = models.DecimalField(max_digits=9, decimal_places=7)
    resemblance_score = models.DecimalField(max_digits=9, decimal_places=7)

class Stroke(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

class Dot(models.Model):
    stroke = models.ForeignKey(Stroke, on_delete=models.CASCADE)
    x = models.DecimalField(max_digits=10, decimal_places=6)
    y = models.DecimalField(max_digits=10, decimal_places=6)
