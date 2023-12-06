from django.core.validators import RegexValidator
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, phonenumber, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given phonenumber,email and password.
        """
        if not phonenumber or not email:
            raise ValueError("Users must have an phonenumber or email address")
        email = self.normalize_email(email)
        user = self.model(phonenumber=phonenumber, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phonenumber, email=None, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given phonenumber, username, email and password.
        """
        user = self.create_user(
            phonenumber,
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    phonenumber = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^(?:\+98|0)?9[0-9]{2}(?:[0-9](?:[ -]?[0-9]{3}){2}|[0-9]{8})$',
                message="Invalid phone number format. Example: +989123456789 or 09123456789",
            ),
        ],
        verbose_name="Phone number",
        unique=True)
    email = models.EmailField(
        max_length=100,
        verbose_name="email address",
    )
    username = models.CharField(max_length=40, null=True, blank=True,
                                help_text="Create the default username using the format firstname_lastname@cofe")
    firstname = models.CharField(max_length=40)
    lastname = models.CharField(max_length=40)
    how_know_us = models.CharField(choices=[("Ch_Tel", "Chanel Telegram"), ("Ins", "Instagram"), ("Web", "Web Site"),
                                            ("Fr", "Friends"), ("Other", "Other items")], default="None")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "phonenumber"
    REQUIRED_FIELDS = ["email", "username"]

    def __str__(self):
        return f"{self.firstname}_{self.lastname}"

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All staff in staff model
        return self.is_admin

    def save(self, *args, **kwargs):
        if self.is_admin:
            self.username = 'admin@Cofe'
        elif not self.username:
            self.username = f"{self.firstname.lower()}_{self.lastname.lower()}@Cofe"
        super().save(*args, **kwargs)

class ValidatorMixin:
     def nationalcode_validator(value):
         """
             Function for checking the number of Iranian national code digits.
             """
         national_code = str(value)
         length = len(national_code)
         if length < 8 or length > 10:
             raise ValidationError('Invalid national code length')


class Staff(models.Model,ValidatorMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff')
    nationalcode = models.CharField(
        max_length=20,
        validators=[ValidatorMixin.nationalcode_validator],
        verbose_name="National Code",
        unique=True
    )
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="birth day", default=date(1380, 1, 1))
    experience = models.IntegerField(null=True, default=None)
    rezome = models.FileField(upload_to='files/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='images/', blank=True, null=True,  storage=FileSystemStorage())
    guarantee = models.CharField(choices=[("Ch", "Check"), ("Prn", "Promissory note"), ("rep", "Representative")],
                                 default="None")

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname}"


class LoginRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    last_time = models.DateTimeField(auto_now=True)
    login_count = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
