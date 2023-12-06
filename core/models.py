from django.db import models
# from other_app.models import User
from cafe.models import Items
from django.contrib.auth.models import User



class Image(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    id_Items = models.ForeignKey(Items, on_delete=models.CASCADE)
    id_User = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    id_Items = models.ForeignKey(Items, on_delete=models.CASCADE)
    id_User = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
