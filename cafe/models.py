from django.db import models

# Create your models here.
class CategoryMeno(models.Model):
    title = models.CharField(max_length=50)
    SERVINGTIME=[
        ("M","morning"),
        ("N","noon"),
        ("E","evening"),
        ("N","night")
    ]
    serving_time=name = models.CharField(max_length=7,choices=SERVINGTIME)

class Items(models.Model):
    category_id = models.ForeignKey(CategoryMeno, on_delete=models.CASCADE,related_name="items")
    title = models.CharField(max_length=100)
    price=models.FloatField()
    deccription=models.TextField(max_length=255)
    status=models.BooleanField()
    LIKES=[
        ("1","very bad"),
        ("2","bad"),
        ("3","good"),
        ("4","very good"),
        ("5","extra good"),
        
    ]
    likes=models.CharField(max_length=10,choices=LIKES)
                             