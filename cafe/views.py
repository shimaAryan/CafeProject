from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404, redirect, Http404, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, View, CreateView
from django.contrib import messages
from .models import Order, Receipt
from cafe.forms.cart_form import OrderForm
from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper
import datetime


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 30 * 24 * 60 * 60  # one month
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None,
    )




class CartView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "cart.html"
    context_object_name = "item_orders"
    success_url = reverse_lazy("cafe:menu")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.GET.get('order_id')

        # Check if the 'selected_items' cookie already exists
        selected_items_cookie = self.request.COOKIES.get('selected_items', '')

        # Split the cookie value into a list of selected item IDs
        selected_item_ids = selected_items_cookie.split(',') if selected_items_cookie else []

        order = get_object_or_404(Order, id=order_id) if order_id else None
        if order:
            items = order.items.annotate(
                item_total=ExpressionWrapper(
                    F('price') * F('number_items') - F('discount'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
            print(items)
            context['items'] = items
            context['subtotal'] = sum(item.item_total for item in items) if items else 0
            context['total'] = context['subtotal'] + order.delivery_cost if order.delivery_cost else context['subtotal']
            context['delivery_cost'] = order.delivery_cost
            context['discount_total'] = sum(item.discount for item in items) if items else 0

            # Add the selected item IDs to the cookie
            for item in items:
                if str(item.id) not in selected_item_ids:
                    selected_item_ids.append(str(item.id))

            # Join the selected item IDs into a comma-separated string
            selected_items_cookie = ','.join(selected_item_ids)

            # Set the 'selected_items' cookie with the updated value
            response = HttpResponseRedirect(self.success_url)
            response.set_cookie('selected_items', selected_items_cookie)
            return response
        else:
            raise Http404("No such order found")

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     order_id = self.request.GET.get('order_id')
    #     order = get_object_or_404(Order, id=order_id) if order_id else None
    #     if order:
    #         items = order.items.annotate(
    #             item_total=ExpressionWrapper(
    #                 F('price') * F('number_items') - F('discount'),
    #                 output_field=DecimalField(max_digits=10, decimal_places=2)
    #             )
    #         )
    #         print(items)
    #         context['items'] = items
    #         context['subtotal'] = sum(item.item_total for item in items) if items else 0
    #         context['total'] = context['subtotal'] + order.delivery_cost if order.delivery_cost else context['subtotal']
    #         context['delivery_cost'] = order.delivery_cost
    #         context['discount_total'] = sum(item.discount for item in items) if items else 0
    #     else:
    #         raise Http404("No such order found")
    #     return context

    

class ReceiptView(LoginRequiredMixin, CreateView):
    template_name = 'cart.html'
    context_object_name = 'receipt'
    success_url = reverse_lazy("cafe:cart")

    def get_queryset(self):
        order_id = Receipt.objects.select_related('order').prefetch_related('items').get(
            id=self.request.POST.get('order_id'))
        print("order:===", order_id)
        return order_id
