from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, View, CreateView
from django.contrib import messages
from .models import Order, Receipt
from cafe.forms.cart_form import OrderForm
from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper


class CartView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "cart.html"
    context_object_name = "item_orders"
    form_class = OrderForm
    success_url = reverse_lazy("User:profile")

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items').annotate(
            item_total=Sum(
                ExpressionWrapper(F('items__price') * F('items__number_items'), output_field=DecimalField()
                                  )
            ),
            subtotal=ExpressionWrapper(
                Coalesce(F('item_total'), Value(0), output_field=DecimalField())
                - Coalesce(F('items__discount'), Value(0), output_field=DecimalField())
                + Coalesce(F('delivery_cost'), Value(0), output_field=DecimalField()), output_field=DecimalField()
            )
        ).order_by('-order_time')
        return queryset

class ReceiptView(LoginRequiredMixin, CreateView):
    template_name = 'cart.html'
    context_object_name = 'receipt'
    success_url = reverse_lazy("cafe:cart")

    def get_queryset(self):
        order_id = Receipt.objects.select_related('order').prefetch_related('items').get(
            id=self.request.POST.get('order_id'))
        print("order:===", order_id)
        return order_id
