from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from core.models import Comment, Image

class CommentModelTests(TestCase):
    def test_comment_creation(self):
        content_type = ContentType.objects.create(model='dummy_model')
        dummy_instance = DummyModel.objects.create()
        comment = Comment.objects.create(
            content='This is a test comment',
            content_type=content_type,
            object_id=dummy_instance.pk
        )

        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.content_type, content_type)
        self.assertEqual(comment.object_id, dummy_instance.pk)

class ImageModelTests(TestCase):
    def test_image_creation(self):
        content_type = ContentType.objects.create(model='dummy_model')
        dummy_instance = DummyModel.objects.create()
        image = Image.objects.create(
            image='path',
            content_type=content_type,
            object_id=dummy_instance.pk
        )

        self.assertEqual(str(image.image), 'path')
        self.assertEqual(image.content_type, content_type)
        self.assertEqual(image.object_id, dummy_instance.pk)
