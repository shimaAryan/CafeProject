from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

CustomUser = get_user_model()


@receiver(m2m_changed, sender=CustomUser.groups.through)
def send_staff_notification(sender, instance, action, reverse, pk_set, **kwargs):
    # Check if the user is added to the 'staff' group
    staff_group = Group.objects.get(name='staff')

    if action == 'post_add' and CustomUser.id in pk_set:
        subject = 'You have been added to the Staff group'
        message = 'Dear staff member, \n\nYou have been added to the Staff group. Thank you for joining us!'
        from_email = "saharmahmoodi01@gmail.com"
        # recipient_list = [user.email for user in staff_users]
        # message = render_to_string('account/staff_added_email.txt', {'user': instance})
        to_email = [CustomUser.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False)
