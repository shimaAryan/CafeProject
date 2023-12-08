from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib import messages
from .models import Order,CategoryMenu,Items
from cafe.forms.cart_form import OrderForm


class OrderItemView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "base.html"
    context_object_name = "item_orders"
    success_url = reverse_lazy("User:profile")
    form_class = OrderForm

    def get_queryset(self):
        print('test')
        return Order.objects.prefetch_related('items').all().order_by('-order_time')

    def get_context_data(self, *, object_list=None, **kwargs):
        print('test2')
        context = super().get_context_data(**kwargs)
        context['all_order_items'] = [order.items for order in context['item_orders']]
        context['form'] = self.form_class
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