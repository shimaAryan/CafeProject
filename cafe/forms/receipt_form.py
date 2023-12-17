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
    user_address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'House number and street name',
        'rows': '2',
    }), max_length=100)
    user_postcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    user_city = forms.ChoiceField(choices=city, widget=forms.Select(attrs={'class': 'form-control'}))

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
        # super(PersonalInfo, self).clean()
        user_postcode = self.cleaned_data.get('user_postcode')
        if len(user_postcode) > 10:
            raise forms.ValidationError("'postcode must be 10 characters'")
            # self._errors['user_postcode'] = self.error_class([
            #     'postcode must be 10 characters'])
        elif not user_postcode.isnumeric():
            raise forms.ValidationError("'postcode must be integer'")
            # self._errors['user_postcode'] = self.error_class([
            #     'postcode must integer'])
        return user_postcode
