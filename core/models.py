from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from other_app.models import User  
from other_app.models import Item



class Comment(models.Model):
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, blank=True, null=True)


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    id_Items = models.ForeignKey(Item, on_delete=models.CASCADE)
    id_User = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    id_Items = models.ForeignKey(Item, on_delete=models.CASCADE)
    id_User = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
