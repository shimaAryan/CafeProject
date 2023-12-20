from django.db import models
import datetime as dt
from django.contrib.auth import get_user_model
from django.urls import reverse
from taggit.managers import TaggableManager
from django.db.models import Count
from account.models import CustomUser

user = get_user_model()


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
    price = models.PositiveIntegerField(default=0)
    description = models.TextField(max_length=255)
    status = models.BooleanField()
    discount = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    like = models.ManyToManyField(user, through='Like', related_name='liked_item')
    tags = TaggableManager()


    def __str__(self):
        return self.title
    
    @staticmethod
    def best_items(id_category=None,count=4):
        if id_category:
            obj_category=CategoryMenu.objects.get(id=id_category)
            result = Items.objects.filter(category_id=obj_category).annotate(num_likes=Count("like")).order_by("-num_likes")[:count]
           
            return result
        else:
            result = Items.objects.annotate(num_likes=Count("like")).order_by("-num_likes")[:count]
           
            return result


    def get_absolute_url(self):
        return reverse('cafe:detail_item', args=[self.id])



class Order(models.Model):
    # class OrderStatus(models.TextChoices):
    #     ORDER = "ORDER", "order"
    #     PAYMENT = "PAYMENT", "payment"
    #     CANCELED = "CANCELED", "Canceled"

    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="user_cart")
    # status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.ORDER)
    status = models.CharField(max_length=10, default="order")
    order_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_time']
        indexes = [
            models.Index(fields=['-order_time'])
        ]

    def get_absolute_url(self):
        return reverse('cafe:cart-receipt', args=[user.id])
    def __str__(self):
        return f" {self.id}"


class OrderItem(models.Model):
    DoesNotExist = None
    quantity = models.PositiveIntegerField(default=1, blank=True)
    delivery_cost = models.PositiveIntegerField(null=True, blank=True, default=0)
    items = models.ManyToManyField(Items, related_name="item_order")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order")

    def __str__(self):
        return f"{self.order.id} "


class Receipt(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='receipt_order')
    delivery_time = models.TimeField(default=dt.time(00, 00))
    delivery_date = models.CharField()


    class Meta:
        ordering = ['-time']
        indexes = [
            models.Index(fields=['-time'])
        ]

    def __str__(self):
        return f"{self.time}"


class Like(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE, related_name="users")
    items = models.ForeignKey(Items, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{user.id}"

    
    @staticmethod
    def is_liked(userr,itemm):
        try:
            Like.objects.get(user=userr, items=itemm)
            return True
        except :
            return False

