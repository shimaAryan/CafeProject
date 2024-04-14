from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from .forms import CommentForm, ImageForm
from .models import Comment, Image




class AddCommentView(FormView):
    template_name = 'AddCommentView.html'
    form_class = CommentForm

    def form_valid(self, form):
        content_type = ContentType.objects.get_for_id(self.kwargs['content_type_id'])
        model_class = content_type.model_class()
        instance = get_object_or_404(model_class, pk=self.kwargs['object_id'])

        comment = form.save(commit=False)
        comment.content_type = content_type
        comment.object_id = self.kwargs['object_id']
        comment.save()

        messages.success(self.request, 'Comment added successfully.')
        return redirect(instance)

    def form_invalid(self, form):
        messages.error(self.request, 'Error adding comment. Please check the form.')
        return HttpResponseForbidden("Invalid request method.")



class AddImageView(FormView):
    template_name = 'AddImageView.html'
    form_class = ImageForm

    def form_valid(self, form):
        content_type = ContentType.objects.get_for_id(self.kwargs['content_type_id'])
        model_class = content_type.model_class()
        instance = get_object_or_404(model_class, pk=self.kwargs['object_id'])

        image = form.save(commit=False)
        image.content_type = content_type
        image.object_id = self.kwargs['object_id']
        image.save()

        messages.success(self.request, 'Image added successfully.')
        return redirect(instance)

    def form_invalid(self, form):
        messages.error(self.request, 'Error adding image. Please check the form.')
        return HttpResponseForbidden("Invalid request method.")

