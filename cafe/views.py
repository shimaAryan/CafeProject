from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib import messages
from .models import Order
from forms.cart_form import OrderForm


class OrderItemView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "cart.html"
    context_object_name = "order"
    form_class = OrderForm
    success_url = reverse_lazy("User:profile")
    ordering = ['-order_time']
