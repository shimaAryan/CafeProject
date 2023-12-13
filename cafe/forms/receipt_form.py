from django.contrib.auth import get_user_model
from django import forms

user = get_user_model()


class PersonalInfo(forms.ModelForm):
    city = (
        ("tehran", "Tehran"),
        ("karaj", "Karaj"),
        ("mashhad", "Mashhad"),
        ("mazandaran", "Mazandaran"),
        ("shiraz", "Shiraz"),
    )
    user_address = forms.CharField(widget=forms.FileInput(), max_length=100)
    user_postcode = forms.IntegerField(widget=forms.IntegerField)
    user_city = forms.ChoiceField(choices=city)

    class Meta:
        model = user
        fields = ["firstname", "lastname", "phonenumber", "email"]

    def clean(self):
        super(PersonalInfo, self).clean()
        user_postcode = self.cleaned_data.get('user_postcode')
        if len(user_postcode) > 10:
            self._errors['user_postcode'] = self.error_class([
                'postcode must be 10 characters'])
