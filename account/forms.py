from django import forms
from django.contrib.auth.forms import AuthenticationForm
from account.models import CustomUser, Staff
from core.models import Comment


class UserRegisterForm(forms.ModelForm):
    """
    Class for Create and handle the User sign up form.in fact this form is create
    for handling Customer.
    """
    choices = [("Ch_Tel", "Chanel Telegram"), ("Ins", "Instagram"), ("Web", "Web Site"), ]
    password_confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Confirm your password",
               "style": "background: transparent !important;", }))

    how_know_us = forms.CharField(widget=forms.Select(choices=choices))

    class Meta:
        model = CustomUser
        fields = ["phonenumber", "email", "firstname", "lastname", "password", "how_know_us"]
        widgets = {
            'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number',
                                                  "style": "background: transparent !important;"}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password',
                                                   "style": "background: transparent !important;"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address',
                                             "style": "background: transparent !important;"}),
            'firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name',
                                                "style": "background: transparent !important;"}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name',
                                               "style": "background: transparent !important;"}),
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
    phonenumber = forms.CharField(
        label='Phone Number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number',
                                      "style": "background: transparent !important;"}), )
    profile_image = forms.ImageField(required=True)

    class Meta:
        model = Staff
        fields = ('nationalcode', 'date_of_birth', 'experience', 'rezome', 'guarantee')

    widgets = {
        'nationalcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your national code',
                                               "style": "background: transparent !important;"}),
        'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter your date of birth',
                                                'type': 'date', "style": "background: transparent !important;"}),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field, widget in self.widgets.items():
            self.fields[field].widget = widget


class CustomAuthenticationForm(AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    phonenumber/password logins.
    """
    username = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "autocomplete": "off",
               'placeholder': 'Enter your phone number or email address',
               "style": "background: transparent !important;"}),
        help_text="Please enter a valid phone number of email address.",
        label='phone number or Email Address')
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control", "autocomplete": "off", 'placeholder': 'Enter your password',
               "style": "background: transparent !important;"}), help_text="forgot your" "password", )


class CommentToManagerForm(forms.ModelForm):
    """
    Class for handel the user comment to Manager.
    """

    class Meta:
        model = Comment
        fields = ('content',)


class UserProfileUpdateForm(forms.ModelForm):
    """
    Class for updating the User profile.
    """

    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'email', 'phonenumber']


class StaffUpdateForm(forms.ModelForm):
    """
    Class for updating the Staff profile.
    """

    class Meta:
        model = Staff
        fields = ('nationalcode', 'date_of_birth', 'experience', 'rezome', 'guarantee')

