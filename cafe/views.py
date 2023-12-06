from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib import messages
from .models import Order, ItemOrder
from cafe.forms.cart_form import OrderForm


class OrderItemView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "order.html"
    context_object_name = "item_orders"
    success_url = reverse_lazy("User:profile")

    def get_queryset(self):
        print('test')
        return Order.objects.prefetch_related('item_order__items').order_by('-order_time')

    def get_context_data(self, *, object_list=None, **kwargs):
        print('test2')
        context = super().get_context_data(**kwargs)


