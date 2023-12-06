from django.db import models
# from account.models import User
import datetime as dt
from django.contrib.auth import get_user_model

<<<<<<< HEAD
from account.models import CustomUser
=======
custom_user = get_user_model()


>>>>>>> 91d24123217ce67702e7574603d5bca1bd6a4d87
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
<<<<<<< HEAD
    discount = models.DecimalField(max_digits=2, decimal_places=2 ,blank=True,default=0)
    number_items = models.PositiveIntegerField(default=1,blank=True)
    like_count = models.PositiveIntegerField(default=0)
    like = models.ManyToManyField(CustomUser, through='Like', related_name='liked_item')
=======
    discount = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    number_items = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    like = models.ManyToManyField(custom_user, through='Like', related_name='liked_item')
>>>>>>> 91d24123217ce67702e7574603d5bca1bd6a4d87

    def __str__(self):
        return self.title


class Order(models.Model):
    DoesNotExist = None
    title = models.CharField(max_length=10, default="cart")
    order_time = models.DateTimeField(auto_now_add=True)
<<<<<<< HEAD
    user_order = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_order")
    number_items = models.PositiveIntegerField()
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
=======
    user_order = models.ForeignKey(custom_user, on_delete=models.CASCADE, related_name="user_order")
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, default=0)
>>>>>>> 91d24123217ce67702e7574603d5bca1bd6a4d87
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
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=5)
    final_price = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        ordering = ['-time']
        indexes = [
            models.Index(fields=['-time'])
        ]


class Like(models.Model):
<<<<<<< HEAD
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="users")
    items = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)
=======
    user = models.ForeignKey(custom_user, on_delete=models.CASCADE, related_name="users")
    items = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)

>>>>>>> 91d24123217ce67702e7574603d5bca1bd6a4d87
