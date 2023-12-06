from django.db import models
# from account.models import User
import datetime as dt
from django.contrib.auth.models import User


class CategoryMeno(models.Model):
    title = models.CharField(max_length=50)
    SERVINGTIME = [
        ("M", "morning"),
        ("N", "noon"),
        ("E", "evening"),
        ("N", "night")
    ]
    serving_time = name = models.CharField(max_length=7, choices=SERVINGTIME)


class Items(models.Model):
    category_id = models.ForeignKey(CategoryMeno, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=100)
    price = models.FloatField()
    deccription = models.TextField(max_length=255)
    status = models.BooleanField()
    LIKES = [
        ("1", "very bad"),
        ("2", "bad"),
        ("3", "good"),
        ("4", "very good"),
        ("5", "extra good"),

    ]
    likes = models.CharField(max_length=10, choices=LIKES)


class Order(models.Model):
    DoesNotExist = None
    order_time = models.DateTimeField(auto_now_add=True)
    user_order = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_order")
    delivery = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True, default=dt.time(00, 00))

    items = models.ManyToManyField(Items, blank=True, related_name="item_order", through='ItemOrder')

    items = models.ManyToManyField(Items, blank=True, related_name="item_order", through='IntermediateModel')

    class Meta:
        ordering = ['-order_time']
        indexes = [
            models.Index(fields=['-order_time'])
        ]


class ItemOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order")
    items = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="items")
    number_of_items = models.PositiveIntegerField()
