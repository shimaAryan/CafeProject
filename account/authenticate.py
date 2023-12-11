from django.contrib.auth import get_user_model

from .models import CustomUser


class PhoneBackend:
    def __init__(self):
        self.UserModel = None

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            self.UserModel = get_user_model()
            user = self.UserModel.objects.get(phonenumber=username)
            if user.check_password(password):
                return user
        except self.UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.UserModel.objects.get(pk=user_id)
        except self.UserModel.DoesNotExist:
            return None


class EmailBackend:

    def __init__(self):
        self.UserModel = None

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            self.UserModel = get_user_model()
            user = self.UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except self.UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.UserModel.objects.get(pk=user_id)
        except self.UserModel.DoesNotExist:
            return None
