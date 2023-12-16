from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from account.models import CustomUser
from config import settings


@receiver(post_save, sender=CustomUser)
def user_group_changed(sender, instance, **kwargs):
    if instance.pk:
        # Check if the group has changed
        original_instance = sender.objects.get(pk=instance.pk)
        print("1"*35, original_instance)
        instance_groups = instance.groups.all()
        customuser_groups = original_instance.groups.all()
        if customuser_groups != instance_groups:
            # Send an email notification to the user
            subject = 'Group Change Notification'
            message = 'Your group has been changed on the site. Check your account for details.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [instance.email]
            send_mail(subject, message, from_email, recipient_list)
