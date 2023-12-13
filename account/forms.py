from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from account.models import CustomUser, Staff, ValidatorMixin


class UserRegisterForm(forms.ModelForm):
    """
    Class for Create and handle the User sign up form.in fact this form is create
    for handling Customer.
    """
    password_confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"class": "form-control", 'placeholder': 'Confirm your password'}))
    how_know_us = forms.CharField(widget=forms.Select(choices=[("Ch_Tel", "Chanel Telegram"),
                                                               ("Ins", "Instagram"),
                                                               ("Web", "Web Site"),
                                                               ]))

    class Meta:
        model = CustomUser
        fields = ["phonenumber", "email", "firstname", "lastname", "password", "how_know_us"]
        widgets = {
            'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Your confirm password and password do not match")
        return password_confirm


class StaffSignUpForm(forms.ModelForm):
    """
    Class for Create and handle the Staff sign up form.
    """
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
    )

    class Meta:
        model = Staff
        fields = "__all__"

    widgets = {
        'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
        'nationalcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your national code'}),
        'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
        'firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
        'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
        'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter your date of birth', 'type': 'date'}),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field, widget in self.widgets.items():
            self.fields[field].widget = widget

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Your confirm password and password do not match")


class CustomAuthenticationForm(AuthenticationForm):
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

