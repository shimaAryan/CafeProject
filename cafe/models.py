from django.db import models
from account.models import User
import datetime as dt
class Order(models.Model):
    order_time = models.DateTimeField(auto_now_add=True)
    user_order = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="user_order")
    delivery = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True, default=dt.time(00, 00))
    items = models.ManyToManyField(Item, blank=True, related_name="item_order", through='IntermediateModel')

    class Meta:
        ordering = ['-order_time']
        indexes = [
            models.Index(fields=['-order_time'])
        ]


class ItemOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order")
    items = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="items")
    number_of_items = models.PositiveIntegerField()

