from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from account.models import CustomUser


class UserRegisterForm(forms.Form):
    phonenumber = forms.CharField(
        widget=forms.TimeInput(attrs={"class": "form-control", 'placeholder': 'Enter your phone number'}),
        help_text="Please enter a valid phonenumber", label='Phone Number', )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", 'placeholder': 'Enter your password'}))
    password2 = forms.CharField(label="confirm password", widget=forms.PasswordInput(
        attrs={"class": "form-control", 'placeholder': 'confirm password'}))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", 'placeholder': 'Enter Email address'}),
        help_text="Please enter a valid email address.", )
    firstname = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", 'placeholder': 'Enter your First Name'}),
        max_length=40, label='First Name', )
    lastname = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", 'placeholder': 'Enter your Last Name'}),
        max_length=40, label='Last Name', )
    how_know_us = forms.CharField(widget=forms.Select(choices=[("Ch_Tel", "Chanel Telegram"),
                                                               ("Ins", "Instagram"),
                                                               ("Web", "Web Site"),
                                                               ]))

    def clean_email(self):
        email_input = self.cleaned_data["email"]
        validator = RegexValidator(
            "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:["
            "a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
        user = CustomUser.objects.filter(email=email_input).exists()
        try:
            validator(email_input)
            if user:
                self.add_error("email", "this email is already exists")
        except ValidationError:
            self.add_error("email", "Invalid email format")
        return email_input

    def clean(self):
        datas = super().clean()
        p1 = datas.get("password")
        p2 = datas.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "your confirm password and password does not match")


class CustomAuthenticationForm (AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    phonenumber/password logins.
    """
    username = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "off",
               'placeholder': 'Enter your phone number or email address'}),
        help_text="Please enter a valid phone number of email address.",
        label='phone number or Email Address')
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control", "autocomplete": "off", 'placeholder': 'Enter your password'}),
        help_text="forgot your "
                  "password", )
#     error_messages = {
#         "invalid_login": (
#             "Please enter a correct %(username)s and password. Note that both "
#             "fields may be case-sensitive."
#         ),
#         "inactive": ("This account is inactive."),
#     }
