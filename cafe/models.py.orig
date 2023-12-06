from django.db import models
# from account.models import User
import datetime as dt
from django.contrib.auth.models import User

<<<<<<< HEAD
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
                             
=======

class CategoryMenu(models.Model):
    title = models.CharField(max_length=50)
    SERVINGTIME = [
        ("M", "morning"),
        ("N", "noon"),
        ("E", "evening"),
        ("N", "night")
    ]
    serving_time = models.CharField(max_length=7, choices=SERVINGTIME)

    def __str__(self):
        return self.title


class Items(models.Model):
    category_id = models.ForeignKey(CategoryMenu, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField(max_length=255)
    status = models.BooleanField()
    discount = models.DecimalField(max_digits=2, decimal_places=2)
    number_items = models.PositiveIntegerField()
    like_count = models.PositiveIntegerField(default=0)
    like = models.ManyToManyField(User, through='Like', related_name='liked_item')

    def __str__(self):
        return self.title


class Order(models.Model):
    DoesNotExist = None
    order_time = models.DateTimeField(auto_now_add=True)
    user_order = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_order")
    number_items = models.PositiveIntegerField()
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True, default=dt.time(00, 00))
    items = models.ForeignKey(Items, on_delete=models.CASCADE, blank=True, related_name="item_order")

    class Meta:
        ordering = ['-order_time']
        indexes = [
            models.Index(fields=['-order_time'])
        ]


class Receipt(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=3)
    final_price = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        ordering = ['-time']
        indexes = [
            models.Index(fields=['-time'])
        ]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    items = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)
>>>>>>> dbf5c2631ab9386061ae16d4a4c7c5d5edf9eb4d
