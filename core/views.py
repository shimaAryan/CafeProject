from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden
from .models import Comment
from django.contrib import messages
from .forms import CommentForm

# Create your views here.


def add_comment(request, content_type_id, object_id):
    if request.method == 'POST':
        content_type = ContentType.objects.get_for_id(content_type_id)
        model_class = content_type.model_class()

        try:
            instance = model_class.objects.get(pk=object_id)
        except model_class.DoesNotExist:
            return HttpResponseForbidden("Invalid content type or object ID.")

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.content_type = content_type
            comment.object_id = object_id
            comment.save()

            messages.success(request, 'Comment added successfully.')
            return redirect(instance)
        else:
            messages.error(request, 'Error adding comment. Please check the form.')

    return HttpResponseForbidden("Invalid request method.")









    def add_image(request):
        pass