from django import forms
from ..models import Order
import datetime as dt

HOUR_CHOICES = [(dt.time(hour=x), '{:02d}:00'.format(x)) for x in range(0, 24)]


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = '__all__'
        widgets = {'delivery_time': forms.Select(choices=HOUR_CHOICES)}

