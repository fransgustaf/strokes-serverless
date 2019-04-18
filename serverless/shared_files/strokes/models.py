import uuid
import json

from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200)
    api_key = models.CharField(max_length=50, null=True)

class DocumentSetting(models.Model):
    default_name = models.CharField(max_length=200, default="A new default document name")

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    @staticmethod
    def save_document_setting(input_document_setting, customer_id):

        input_id=-1

        document_setting = None
        document_settings = DocumentSetting.objects.filter(id=input_id)
        if document_settings.exists():
            document_setting = document_settings.first()
        else:
            document_setting = DocumentSetting(default_name=input_document_setting['default_name'], customer_id=customer_id)
            document_setting.save()

        for input_page_setting in input_document_setting['pageSettings']:
            PageSetting.save_page_setting(document_setting.id, input_page_setting, customer_id)

        return document_setting


class PageSetting(models.Model):
    document_setting = models.ForeignKey(DocumentSetting, on_delete=models.CASCADE)
    number = models.IntegerField(null=False)
    width = models.DecimalField(max_digits=20, decimal_places=6)
    height = models.DecimalField(max_digits=20, decimal_places=6)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    @staticmethod
    def save_page_setting(document_setting_id, input_page_setting, customer_id):
        input_id=-1

        page_setting = None
        page_settings = PageSetting.objects.filter(id=input_id)
        if page_settings.exists():
            page_setting = page_settings.first()
        else:
            page_setting = PageSetting(document_setting_id=document_setting_id, number=input_page_setting['number'], width=input_page_setting['width'], height=input_page_setting['height'], customer_id=customer_id)
            page_setting.save()

        print(input_page_setting['fieldSettings'])

        for input_field_setting in input_page_setting['fieldSettings']:
            print(input_field_setting)
            FieldSetting.save_field_setting(page_setting.id, input_field_setting, customer_id)

        return page_setting.id


class FieldSetting(models.Model):
    page_setting = models.ForeignKey(PageSetting, on_delete=models.CASCADE)
    x = models.DecimalField(max_digits=20, decimal_places=6)
    y = models.DecimalField(max_digits=20, decimal_places=6)
    width = models.DecimalField(max_digits=20, decimal_places=6)
    height = models.DecimalField(max_digits=20, decimal_places=6)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    def get_recognition_setting(self):
        recognition_settings = RecognitionSetting.objects.filter(field_setting_id=self.id)
        recognition_setting = None
        if recognition_settings.exists():
            recognition_setting = recognition_settings.first()
        return recognition_setting

    @staticmethod
    def save_field_setting(page_setting_id, input_field_setting, customer_id):
        input_id=-1

        field_setting = None
        field_settings = FieldSetting.objects.filter(id=input_id)
        if field_settings.exists():
            field_setting = field_settings.first()
        else:
            field_setting = FieldSetting(page_setting_id=page_setting_id, x=input_field_setting['x'], y=input_field_setting['y'], width=input_field_setting['width'], height=input_field_setting['height'], customer_id=customer_id)
            field_setting.save()

        RecognitionSetting.save_recognition_setting(field_setting.id, input_field_setting['recognitionSetting'], customer_id)

        return field_setting.id


class RecognitionSetting(models.Model):
    field_setting = models.ForeignKey(FieldSetting, on_delete=models.CASCADE)
    input_mode = models.CharField(max_length=20, default="CURSIVE")
    input_type = models.CharField(max_length=20, default="MULTI_LINE_TEXT")
    language = models.CharField(max_length=20, default="en_US")

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    @staticmethod
    def save_recognition_setting(field_setting_id, input_recognition_setting, customer_id):
        input_id=-1

        recognition_setting = None
        recognition_settings = RecognitionSetting.objects.filter(id=input_id)
        if recognition_settings.exists():
            recognition_setting = recognition_settings.first()
        else:
            recognition_setting = RecognitionSetting(field_setting_id=field_setting_id, input_mode=input_recognition_setting['input_mode'], input_type=input_recognition_setting['input_type'], language=input_recognition_setting['language'], customer_id=customer_id)
            recognition_setting.save()

        return recognition_setting.id

    
class Document(models.Model):
    name = models.CharField(max_length=200)
    identifier = models.CharField(max_length=50, default=uuid.uuid4)
    document_setting = models.ForeignKey(DocumentSetting, on_delete=models.CASCADE)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    @staticmethod
    def get_document(document_id, customer_id):
        return Document.objects.get(id=document_id, customer_id=customer_id)

    def get_pages(self):
        return self.page_set.all()

    @staticmethod
    def save_document(event_body, identifier, customer_id):
        document = None
        document_setting = None
        create_document = False
        if identifier:
            documents = Document.objects.filter(identifier=identifier)
            if documents.exists():
                document = documents.first()
                document_setting = DocumentSetting.objects.get(id=document.document_setting_id, customer_id=customer_id)
            else:
                create_document = True
        else:
            create_document = True
            identifier = uuid.uuid4()

        if create_document:
            document_setting_id = event_body['documentSettingId']
            document_setting = DocumentSetting.objects.get(id=document_setting_id, customer_id=customer_id)
            document = Document(document_setting_id=document_setting.id, name=document_setting.default_name, identifier=identifier, customer_id=customer_id)
            document.save()

        return document


class Page(models.Model):
    page_setting = models.ForeignKey(PageSetting, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, default=uuid.uuid4)
    number = models.IntegerField(null=False)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    def get_fields(self):
        return self.field_set.all()

    def get_strokes_as_json(self):
        strokes_data = []
        for stroke in self.stroke_set.all():
            stroke_data = []
            for dot in stroke.dot_set.all():
                #stroke.append(serializers.serialize("json", [stroke, ]))
                stroke_data.append({"x": float(dot.x), "y": float(dot.y)})
            strokes_data.append({"dots": stroke_data})
        return strokes_data


    @staticmethod
    def save_page(customer_id, input_page, page_address, document_identifier):
        page_number = None
        if 'number' in input_page:
            page_number = input_page['number']

        documents = Document.objects.filter(identifier=document_identifier, customer_id=customer_id)

        if documents.exists():
            document = documents.first()
        else:
            raise ValueError("Document doesn't exist")

        pages = Page.objects.filter(document_id=document.id, number=page_number, customer_id=customer_id)

        if pages.exists():
            page = pages.first()
            print("page exists {0} {1}".format(page.id, page.address))
            if page_number is not None:
                page.number = page_number
            page.save()
        else:
            page_setting = PageSetting.objects.get(document_setting_id=document.document_setting_id, number=1 if page_number is None else page_number, customer_id=customer_id)
            page = Page(page_setting_id=page_setting.id, document_id=document.id, address=uuid.uuid4() if page_address is None else page_address, number= 1 if page_number is None else page_number, customer_id=customer_id)
            page.save()
            for field_setting in FieldSetting.objects.filter(page_setting_id=page_setting.id, customer_id=customer_id):
                field = Field(page_id=page.id, field_setting_id=field_setting.id, customer_id=customer_id)
                field.save()
            print("new page {0} {1}".format(page.id, page.address))

        return page


    def get_myscript_json(self, field, field_setting, recognition_setting):
        strokes_data = []
        print("Field setting x: {0}, y: {1}, width: {2}, heigth: {3}".format(field_setting.x, field_setting.y, field_setting.width, field_setting.height))
        for stroke in self.stroke_set.all():
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


class Field(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    field_setting = models.ForeignKey(FieldSetting, on_delete=models.CASCADE)
    recognition_setting = models.ForeignKey(RecognitionSetting, on_delete=models.CASCADE, null=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    def get_field_setting(self):
        return FieldSetting.objects.get(id=self.field_setting_id)


class RecognitionResult(models.Model):
    field = models.OneToOneField(Field, on_delete=models.CASCADE, primary_key=False)
    selected_candidate_id = models.IntegerField(null=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    # {"result":{"textSegmentResult":{"selectedCandidateIdx":0,"candidates":[{"label":"i. It.","normalizedScore":1.0,"resemblanceScore":0.5168961,"children":null}]}},"instanceId":"296cbe8b-3018-4b6b-bec0-a44b63a8fe7d"}
    @staticmethod
    def save_recognition_result(field_id, result, customer_id):
        result_json = json.loads(result)

        if 'textSegmentResult' in result_json['result']:
            RecognitionResult.objects.filter(field_id=field_id, customer_id=customer_id).delete()
            recognition_result = RecognitionResult(field_id=field_id, selected_candidate_id=int(result_json['result']['textSegmentResult']['selectedCandidateIdx']), customer_id=customer_id)
            recognition_result.save()

            for candidate in result_json['result']['textSegmentResult']['candidates']:
                recognition_candidate = RecognitionCandidate(recognition_result_id=recognition_result.id, value=candidate['label'], normalized_score=candidate['normalizedScore'], resemblance_score=candidate['resemblanceScore'], customer_id=customer_id)
                recognition_candidate.save()


class RecognitionCandidate(models.Model):
    recognition_result = models.ForeignKey(RecognitionResult, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    normalized_score = models.DecimalField(max_digits=9, decimal_places=7)
    resemblance_score = models.DecimalField(max_digits=9, decimal_places=7)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')


class Stroke(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')

    @staticmethod
    def save_by_address(address, input_stroke, customer_id):
        pages = Page.objects.filter(address=address, customer_id=customer_id)
        if not pages.exists:
            raise ValueError('Page does not exist')

        page = pages.first()
        stroke = Stroke(page_id=page.id, customer_id=customer_id)
        stroke.save()
        dots_to_insert = []
        for input_dot in input_stroke['dots']:
            dots_to_insert.append(Dot(stroke_id=stroke.id, x=input_dot['x'], y=input_dot['y'], customer_id=customer_id))

            Dot.objects.bulk_create(dots_to_insert)

        return stroke


    @staticmethod
    def save_by_document_page(document_identifier, number, input_stroke, customer_id):
        documents = Document.objects.filter(identifier=document_identifier, customer_id=customer_id)
        if not documents.exists:
            raise ValueError('Document does not exist')
        document = documents.first()
        pages = Page.objects.filter(document_id=document.id, number=number, customer_id=customer_id)
        if not pages.exists:
            raise ValueError('Page does not exist')

        page = pages.first()
        stroke = Stroke(page_id=page.id, customer_id=customer_id)
        stroke.save()
        dots_to_insert = []
        for input_dot in input_stroke['dots']:
            dots_to_insert.append(Dot(stroke_id=stroke.id, x=input_dot['x'], y=input_dot['y'], customer_id=customer_id))

            Dot.objects.bulk_create(dots_to_insert)

        return stroke


class Dot(models.Model):
    stroke = models.ForeignKey(Stroke, on_delete=models.CASCADE)
    x = models.DecimalField(max_digits=10, decimal_places=6)
    y = models.DecimalField(max_digits=10, decimal_places=6)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('id', 'customer')
