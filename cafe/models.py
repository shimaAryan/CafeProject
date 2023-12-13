from django.db import models
# from account.models import User
import datetime as dt
from django.contrib.auth import get_user_model

from account.models import CustomUser


class ServingTime(models.Model):
    time = models.CharField(max_length=7)

    def __str__(self):
        return self.time


# class CategoryMenu(models.Model):
#     title = models.CharField(max_length=50)
#     serving_time = models.ManyToManyField(ServingTime)

class CategoryMenu(models.Model):
    title = models.CharField(max_length=50)

    serving_time = models.ManyToManyField(ServingTime)

    def __str__(self):
        return self.title


class Items(models.Model):
    category_id = models.ForeignKey(CategoryMenu, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    description = models.TextField(max_length=255)
    status = models.BooleanField()
    discount = models.PositiveIntegerField(default=0)
    number_items = models.PositiveIntegerField(default=1)
    like_count = models.PositiveIntegerField(default=0)
    like = models.ManyToManyField(CustomUser, through='Like', related_name='liked_item')

    def __str__(self):
        return self.title


from decimal import Decimal


class Order(models.Model):
    DoesNotExist = None
    title = models.CharField(max_length=10, default="cart")
    order_time = models.DateTimeField(auto_now_add=True)
    user_order = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_order")
    number_items = models.PositiveIntegerField(default=1, blank=True)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True, default=dt.time(00, 00))
    items = models.ManyToManyField(Items, related_name="item_order")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-order_time']
        indexes = [
            models.Index(fields=['-order_time'])
        ]


class Receipt(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order')

    class Meta:
        ordering = ['-time']
        indexes = [
            models.Index(fields=['-time'])
        ]

    def __str__(self):
        return self.order.title


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="users")
    items = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.id, self.items.title
