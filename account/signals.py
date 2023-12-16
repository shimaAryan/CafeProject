from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from account.models import CustomUser
from config import settings


# @receiver(post_save, sender=CustomUser)
# def user_group_changed(sender, instance, **kwargs):
#     if instance.pk:
#         # Check if the group has changed
#         original_instance = sender.objects.get(pk=instance.pk)
#         print("1" * 35, original_instance)
#         instance_groups = instance.is_customer
#         customuser_groups = original_instance.is_customer
#         if instance_groups != customuser_groups and instance.is_customer == False:
#             # Send an email notification to the user
#             subject = 'Group Change Notification'
#             message = 'Your group has been changed on the site. Check your account for details.'
#             from_email = settings.EMAIL_HOST_USER
#             recipient_list = [instance.email]
#             send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=CustomUser)
def send_email_on_is_customer_change(sender, instance, **kwargs):
    if instance.is_customer is False:
        send_customer_disabled_email(instance)

def send_customer_disabled_email(user):
    subject = 'Account Deactivated'
    html_message = render_to_string('account/active.html', {'user': user})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = [user.email]
    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
