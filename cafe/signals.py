from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def create_order(sender,instance,created, **kwargs):
        # user = kwargs.get('user')
        # if user:
        #     order, created = Order.objects.get_or_create(user=user)
        if sender == Order:
            user = instance.user
        else:
            user = instance

        if created and user:
            order, created = Order.objects.get_or_create(user=user)