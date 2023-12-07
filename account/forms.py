from django import forms


class UserLoginForm(forms.Form):
    phonenumber = forms.CharField(widget=forms.TextInput(
        attrs={"autocomplete": "off", 'placeholder': 'Enter your phone number or email adress'}),
                                   help_text="Please enter a valid phone number of email address.",
                                   label='phone number or Email Adress')
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={"autocomplete": "off", 'placeholder': 'Enter your password'}),
                               help_text="forgot your "
                                         "password", )
