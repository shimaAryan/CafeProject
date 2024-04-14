from django import forms
from .models import Comment, Image


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['content']



class ImageForm(forms.ModelForm):
    
    class Meta:
        model = Image
        fields = ['image']