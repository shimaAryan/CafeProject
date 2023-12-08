from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.contrib import messages
from .models import Order,CategoryMenu,Items,Receipt
from cafe.forms.cart_form import OrderForm


class OrderItemView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "base.html"
    # template_name = "cart.html"
    context_object_name = "item_orders"
    success_url = reverse_lazy("User:profile")
    form_class = OrderForm

    def get_queryset(self):

        return Order.objects.prefetch_related('items').all().order_by('-order_time')

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super().get_context_data(**kwargs)
        context['all_order_items'] = [order.items for order in context['item_orders']]
        context['form'] = self.form_class
        print(context['all_order_items'])
        return context


class CategoryItems(LoginRequiredMixin,ListView):
    model = CategoryMenu
    context_object_name = 'category'
    template_name='category.html'

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self,*, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        for category in context["category"]:
            context[category.title]=Items.objects.filter(category_id=category.id)
class ReceiptView(LoginRequiredMixin, View):
    template_name = 'receipt.html'
    context_object_name = 'receipt'
    success_url = reverse_lazy("cafe:cart")
    form_class = OrderForm

    def get(self, request):
        receipt_item = Receipt.objects.select_related('order').get(id=request.POST.get('id'))
