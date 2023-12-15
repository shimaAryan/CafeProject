from django.test import TestCase
from core.forms import CommentForm, ImageForm

class FormTests(TestCase):
    def test_valid_form(self):
        data = {'field1': 'value1', 'field2': 'value2'}
        form = Form(data=data)

        self.assertTrue(form.is_valid())




    def test_invalid_form(self):
        data = {
            'field1': '', # it is wrong testing !!
            'field2': 'value2',
        }
        form = Form(data=data)

        self.assertFalse(form.is_valid())
