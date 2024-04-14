from django.test import TestCase
from django.urls import reverse
from core.models import Comment, Image
from core.views import add_comment, add_image

class YourViewTests(TestCase):
    def setUp(self):
        YourModel.objects.create(field1='value1', field2='value2')  
        

    def test_view_status_code(self):
        url = reverse('add_comment_url', args=[content_type_id, object_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)



    def test_view_template_used(self):
        url = reverse('add_comment', args=[content_type_id, object_id])
        response = self.client.get(url) 

        self.assertTemplateUsed(response, 'path.html') 
