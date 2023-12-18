from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator, validate_email
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone


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
        Creates and saves a superuser with the given phonenumber, nickname, email and password.
        """
        user = self.create_user(
            phonenumber,
            email,
            password=password,
        )
        user.is_admin = True
        user.is_customer = False
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phonenumber = models.CharField(max_length=50, validators=[RegexValidator(
        regex=r'^(?:\+98|0)?9[0-9]{2}(?:[0-9](?:[ -]?[0-9]{3}){2}|[0-9]{8})$',
        message="Invalid phone number format. Example: +989123456789 or 09123456789", ),
    ], verbose_name="Phone number", unique=True)
    email = models.EmailField(max_length=100, verbose_name="email address", validators=[validate_email],
                              unique=True
                              )
    nickname = models.CharField(max_length=40, null=True, blank=True,
                                help_text="Create the default nickname using the format firstname_lastname@cofe")
    firstname = models.CharField(max_length=40)
    lastname = models.CharField(max_length=40)
    how_know_us = models.CharField(max_length=30,
                                   choices=[("Ch_Tel", "Chanel Telegram"), ("Ins", "Instagram"), ("Web", "Web Site"),
                                            ("Fr", "Friends"), ("Other", "Other items")], default="other", null=True)
    is_customer = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "phonenumber"
    REQUIRED_FIELDS = ["email", ]

    def __str__(self):
        return f"{self.firstname}_{self.lastname}"

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True
        # return super().has_perm(perm)

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        # return super().has_module_perms(app_label)
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All staff in staff model
        if not self.is_customer:
            return not self.is_customer

    @is_staff.setter
    def is_staff(self, value):
        self._is_staff = value

    def save(self, *args, **kwargs):
        if self.is_admin:
            self.nickname = 'admin@Cofe'
        elif not self.nickname:
            self.nickname = f"{self.firstname.lower()}_{self.lastname.lower()}@Coffee"
        super().save(*args, **kwargs)


    @receiver(post_migrate, sender=None)
    def handle_group(sender, **kwargs):
        app_config = apps.get_app_config("cafe")
        app_config2 = apps.get_app_config("core")
        app_config3 = apps.get_app_config("account")
        models_app = list(app_config.get_models())
        account_model = app_config3.get_model("CustomUser")
        models_app.append(account_model)
        CommentModel = app_config2.get_model("Comment")
        models_app.append(CommentModel)
        group, created = Group.objects.get_or_create(name="customer")
        for model in models_app:
            content_type = ContentType.objects.get_for_model(model)
            model_permission = Permission.objects.filter(content_type=content_type)
            for perm in model_permission:
                list_view_model = ['Items', 'CategoryMenu', 'Order', 'Receipt']
                if model.__name__ in list_view_model:
                    view_perm = 'view_' + model.__name__.lower()
                    if perm.codename == view_perm:
                        group.permissions.add(perm)
                if model.__name__ == 'CustomUser':
                    pass
                else:
                    group.permissions.add(perm)


class ValidatorMixin:
    def nationalcode_validator(value):
        """
             Function for checking the number of Iranian national code digits.
             """
        national_code = str(value)
        length = len(national_code)
        if length < 8 or length > 10:
            raise ValidationError('Invalid national code length')


class Staff(models.Model, ValidatorMixin):
    """
   Models for managing information of Staff in coffee .
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff')
    nationalcode = models.CharField(max_length=50, validators=[ValidatorMixin.nationalcode_validator],
                                    verbose_name="National Code", unique=True)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="birth day",
                                     default=timezone.now)
    experience = models.IntegerField(null=True, default=None)
    rezome = models.FileField(upload_to='files/', blank=True, null=True, default=None)
    # profile_image = models.ImageField(upload_to='images/', blank=True, null=True, storage=FileSystemStorage(),
    #                                   default=None)
    guarantee = models.CharField(choices=[("Ch", "Check"), ("Prn", "Promissory note"), ("rep", "Representative")],
                                 default='check', null=True, max_length=20)

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname}"

    def save(self, *args, **kwargs):
        CustomUser.is_staff, CustomUser.is_customer, CustomUser.is_active = True, False, True
        super().save(*args, **kwargs)

    @receiver(post_migrate, sender=None)
    def handle_group(sender, **kwargs):
        installed_apps = ['account', 'cafe', 'core']
        for app in installed_apps:
            app_config = apps.get_app_config(app)
            models_app = app_config.get_models()
            group, created = Group.objects.get_or_create(name="staff")
            for model in models_app:
                if model.__name__ != "Staff":
                    content_type = ContentType.objects.get_for_model(model)
                    model_permission = Permission.objects.filter(content_type=content_type)
                    for perm in model_permission:
                        group.permissions.add(perm)
#

class LoginRecord(models.Model):
    """
   Models to observe User's login  in coffee website.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    last_time = models.DateTimeField(auto_now=True)
    login_count = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
