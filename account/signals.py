from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from account.models import CustomUser
from config import settings


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
