from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser


class EmailBackend(ModelBackend) :

    def __init__(self):
        self.UserModel = CustomUser

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = self.UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except self.UserModel.DoesNotExist:
            return None

