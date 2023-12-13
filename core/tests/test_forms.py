from django.test import TestCase
from core.forms import CommentForm, ImageForm

class YourFormTests(TestCase):
    def test_valid_form(self):
        data = {'field1': 'value1', 'field2': 'value2'}
        form = YourForm(data=data)

        self.assertTrue(form.is_valid())




    def test_invalid_form(self):
        data = {}
        form = YourForm(data=data)
        
        self.assertFalse(form.is_valid())
