from django.contrib.auth import get_user_model
from django import forms
from cafe.models import Receipt
import datetime as dt

user = get_user_model()


class PersonalInfo(forms.ModelForm):
    city = (
        ("CA", "Los Angeles"),
        ("IL", "Chicago"),
        ("TX", "Houston"),
        ("AZ", "Phoenix"),
        ("CA", "San Diego"),
    )
    user_address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'House number and street name',
        'rows': '2',
    }), max_length=100, required=True)
    user_postcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
                                    required=True,help_text="postcode should be number and 10 characters")
    user_city = forms.ChoiceField(choices=city, widget=forms.Select(attrs={'class': 'form-control'}),
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
    delivery_date = forms.CharField(label="pick the day", widget=forms.Select(choices=DAY_SELECTION, attrs={'class': 'form-control'}))
    delivery_time = forms.TimeField(label="pick the time", widget=forms.Select(choices=HOUR_CHOICES, attrs={'class': 'form-control'}))
    class Meta:
        model = Receipt
        fields = ['delivery_date', 'delivery_time']