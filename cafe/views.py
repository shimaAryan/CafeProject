from typing import Any
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, View,DetailView,CreateView
from django.contrib import messages
from .models import Order,CategoryMenu,Items,Receipt
from cafe.forms.cart_form import OrderForm
from core.models import Image
from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper
from django.contrib.contenttypes.models import ContentType


class CartView(LoginRequiredMixin, ListView):
    model = Order
    
    template_name = "cart.html"
    context_object_name = "item_orders"
    form_class = OrderForm
    success_url = reverse_lazy("User:profile")

   


class CategoryItems(ListView):
    model = CategoryMenu
    context_object_name = "categorys"
    template_name='menu1.html'

    def get_queryset(self):
        return self.model.objects.prefetch_related("items").all()

    def get_context_data(self,*, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["images"]= Image.objects.filter( content_type=ContentType.objects.get_for_model(Items))
        

        return context
class DetailItemView(LoginRequiredMixin,DetailView):
    model=Items
    context_object_name="item"
    template_name="detail_item.html"

    # def handle_no_permission(self):
    #      return render(request, 'unauthorized_access.html', {})
    
    def get_object(self, queryset=None):
        idd = self.kwargs.get('pk')
       
        return Items.objects.get(id=idd)

    def get_context_data(self,*, object_list=None, **kwargs):
            context = super().get_context_data(**kwargs)
            
            context["image"]=Image.objects.get(object_id=self.kwargs.get('pk'))

            return context

class ReceiptView(LoginRequiredMixin, View):
    template_name = 'receipt.html'
    context_object_name = 'receipt'
    success_url = reverse_lazy("cafe:cart")

    def get_queryset(self):
        order_id = Receipt.objects.select_related('order').prefetch_related('items').get(
            id=self.request.POST.get('order_id'))
        print("order:===", order_id)
        return order_id
