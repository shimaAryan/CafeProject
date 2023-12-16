from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import Group


from account.models import Staff


@receiver(m2m_changed, sender=Staff.groups.through)
def send_staff_notification(sender, instance, action, reverse, pk_set, **kwargs):
    # Check if the user is added to the 'staff' group
    user_staff = Group.objects.get(name='staff')
    print("2" * 60, user_staff)
    if action == 'post_add' and user_staff.id in pk_set:
        print("2" * 60, pk_set)
        subject = 'You have been added to the Staff group'
        message = 'Dear staff member, \n\nYou have been added to the Staff group. Thank you for joining us!'
        from_email = "saharmahmoodi01@gmail.com"
        print("1" * 60, instance.email)
        to_email = [instance.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False)
