from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib import messages
from .models import Order, ItemOrder
from cafe.forms.cart_form import OrderForm




class OrderItemView(LoginRequiredMixin, ListView):
    model = ItemOrder
    template_name = "order.html"
    context_object_name = "item_orders"
    form_class = OrderForm
    success_url = reverse_lazy("User:profile")

    def get_queryset(self):
        # Assuming you pass the 'order_id' as an URL parameter
        order_id = self.kwargs.get('order_id')
        # Retrieve the associated Order using the passed order_id
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            # Handle the case where the order does not exist if necessary
            return ItemOrder.objects.none()

        # Filter ItemOrder objects for the given order and sort them by 'number_of_items'
        return order.item_order.all().order_by('-number_of_items')
