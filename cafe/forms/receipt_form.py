from django.contrib.auth import get_user_model
from django import forms
from cafe.models import Receipt
import datetime as dt
import requests
user = get_user_model()


class PersonalInfo(forms.ModelForm):
    user_address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'House number and street name',
        'rows': '2',
    }), max_length=100, required=True)
    user_postcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
                                    required=True, help_text="postcode should be number and 10 characters")
    user_city = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}),
                                  required=True)

    class Meta:
        model = user
        fields = ["firstname", "lastname", "phonenumber", "email"]
        widgets = {
            'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'firstname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'lastname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_city'].choices = self.get_city_choices()

    @staticmethod
    def get_city_choices():
        url = 'https://countriesnow.space/api/v0.1/countries/cities'
        data = {
            "country": "Iran"
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            cities_data = response.json()
            cities_choices = [(city[1:], city[1:]) for city in cities_data['data']]
            return cities_choices
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    def clean_user_postcode(self):
        user_postcode = self.cleaned_data.get('user_postcode')
        if len(user_postcode) > 10:
            raise forms.ValidationError("'postcode must be 10 characters'")
        elif not user_postcode.isnumeric():
            raise forms.ValidationError("'postcode must be integer'")
            # self._errors['user_postcode'] = self.error_class([
            #     'postcode must integer'])
        return user_postcode


class DeliveryTime(forms.ModelForm):
    HOUR_CHOICES = [(dt.time(hour=x), '{:02d}:00'.format(x)) for x in range(8, 21)]

    DAY_SELECTION = (
        ("sat", "Saturday"),
        ("sun", "Sunday"),
        ("mon", "Monday"),
        ("tues", "Tuesday"),
        ("wed", "Wednesday"),
        ("fri", "Friday"),
    )
    delivery_date = forms.CharField(label="pick the day",
                                    widget=forms.Select(choices=DAY_SELECTION, attrs={'class': 'form-control'}))
    delivery_time = forms.TimeField(label="pick the time",
                                    widget=forms.Select(choices=HOUR_CHOICES, attrs={'class': 'form-control'}))

    class Meta:
        model = Receipt
        fields = ['delivery_date', 'delivery_time']
