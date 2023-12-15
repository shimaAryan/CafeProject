import json
from json import JSONDecodeError
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, Http404, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView
from django.contrib import messages
import datetime
from django.views.generic import ListView, View, DetailView, TemplateView
from django.contrib import messages
from .models import Order, CategoryMenu, Items, Receipt
from cafe.forms.cart_form import OrderForm
from django.contrib.contenttypes.models import ContentType
from core.models import Image
from .forms import search_form, receipt_form
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from .models import *
from django.http import JsonResponse

user = get_user_model()

class ContextMixin:
    def get_context(self):
        pass
class CartView(LoginRequiredMixin, View):
    template_name = "cart.html"

    def get_context_data(self, user, session_data):
        context = {}
        if not user or not user.is_authenticated:
            messages.error(self.request, "You must have an account and be logged in", "danger")
            return redirect("account:User_login")
        else:
            try:
                order, created = Order.objects.get_or_create(user=user)
                order_items = OrderItem.objects.filter(order=order)

                if order.status == "ORDER":
                    context = {
                        'item_data': session_data,
                        'order': order,
                        'item_total': 0,
                        'subtotal': 0,
                        'total': 0,
                        'discount_total': 0,
                        'delivery_cost': 0,
                    }

                    for item in session_data:
                        quantity = item.get('quantity', 0)
                        price = item.get('price', 0)
                        discount = item.get('discount', 0)
                        item_total = quantity * price - discount
                        item['item_total'] = item_total
                        context['discount_total'] += discount
                        context['subtotal'] += item_total
                        context['delivery_cost'] = item_total * 2

                    context['total'] = context['subtotal'] + context['delivery_cost']
                else:
                    return HttpResponse("you dont have any order items in your cart ")

            except OrderItem.DoesNotExist:
                context['error'] = "Order Items does not exist"
            except Order.DoesNotExist:
                context['error'] = "Order does not exist"
        print("*_"*30, context)
        return context

    def get(self, request, *args, **kwargs):
        session_order = request.session.get('order', [])
        context = self.get_context_data(request.user, session_order) if session_order else {
            'error': "Order does not exist"}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            new_order = json.loads(request.body)
            session_order = request.session.get('order', [])
            if new_order not in session_order:
                session_order.append(new_order)
                request.session['order'] = session_order
                request.session.modified = True
            return JsonResponse({'message': 'Order has been added successfully'})
        except JSONDecodeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# ------------------------------------------------------------------------------------

class ReceiptView(CartView, FormView):
    template_name = 'checkout.html'
    form_class = receipt_form.PersonalInfo
    success_url = reverse_lazy("cafe:cart")
    success_message = "Your information has been successfully registered"

    def dispatch(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user1 = get_object_or_404(user, id=user_id)
        if not user1 == request.user:
            messages.error(request, "You must be logged in", "danger")
            return redirect("account:User_login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        payment = form.save(commit=False)
        for field_name, field_value in form.cleaned_data.items():
            self.request.session[field_name] = field_value
        messages.success(self.request, self.success_message, 'success')
        return super().form_valid(form)

    def get_context(self,**kwargs):
        context = self.get_context_data(self.request.user, self.request.session.get('order', []))
        if not context:
            raise Http404("No such order found")
        print("!!!!!!!!!",context)
        # order['order'] = context
        return render()

    @staticmethod
    def item_search(self, request):
        items = request.GET.get("items")
        results = []
        if "items":
            form = search_form.SearchForm(request.GET)
            if form.is_valid():
                items = form.cleaned_data["items"]
                results = (Items.objects.annotate(similarity=Greatest(
                    TrigramSimilarity("title", items),
                    TrigramSimilarity("description", items), ))
                           .filter(similarity__gt=0.1).order_by("-similarity"))

        context = {
            "item_search": items,
            "results": results
        }
        return render(request, self.template_name, context)


# -----------------------------------------------------------------------
# class ReceiptView(LoginRequiredMixin, SuccessMessageMixin, FormView, CartView):
#     template_name = 'checkout.html'
#     context_object_name = 'receipt'
#     success_url = reverse_lazy("cafe:cart")
#     form_class = receipt_form.PersonalInfo
#     success_message = "Your information has been successfully registered"
#     def setup(self, request, *args, **kwargs):
#         self.user_id = get_object_or_404(user, id=kwargs["id"])
#         return super().setup(request, *args, **kwargs)
#     def dispatch(self, request, *args, **kwargs):
#         user_pk = self.user_id
#         if not user_pk == request.user.id:
#             messages.error(request, "you must be logged in", "danger")
#             return redirect("account:login")
#         return super().dispatch(request, *args, **kwargs)
# def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     order = self.request.session.get('order')
#     if order:
#         context.update({
#             "subtotal": order['subtotal'],
#             "total": order['total'],
#             "delivery_cost": order['delivery_cost'],
#             "discount_total": order['discount_total'],
#             'form': self.form_class(),
#         })
#     else:
#         raise Http404("No such order found")
#     return context
#
# def get(self, request, *args, **kwargs):
#     context = self.get_context_data()
#     return render(request, self.template_name, context)
#
# def form_valid(self, form):
#     peyment = form.save(commit=False)
#     for field_name, field_value in form.cleaned_data.items():
#         self.request.session[field_name] = field_value
#     messages.success(self.request, self.success_message, 'success')
#     return super().form_valid(form)
#
# @staticmethod
# def item_search(self, request):
#     items = request.GET.get("items")
#     results = []
#     if "items":
#         form = search_form.SearchForm(request.GET)
#         if form.is_valid():
#             items = form.cleaned_data["items"]
#             results = (Items.objects.annotate(similarity=Greatest(
#                 TrigramSimilarity("title", items),
#                 TrigramSimilarity("description", items), ))
#                        .filter(similarity__gt=0.1).order_by("-similarity"))
#
#     context = {
#         "item_search": items,
#         "results": results
#     }
#     return render(request, self.template_name, context)


class CategoryItems(ListView):
    model = CategoryMenu
    context_object_name = "categorys"
    template_name = 'menu1.html'

    def get_queryset(self):
        return self.model.objects.prefetch_related("items").all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))

        return context


class DetailItemView(LoginRequiredMixin, DetailView):
    model = Items
    context_object_name = "item"
    template_name = "detail_item.html"

    # def handle_no_permission(self):
    #      return render(request, 'unauthorized_access.html', {})

    def get_object(self, queryset=None):
        idd = self.kwargs.get('pk')

        return Items.objects.get(id=idd)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image"] = Image.objects.get(object_id=self.kwargs.get('pk'))
        return context


def index(request):
    return render(request, 'index.html')


class HomeView(TemplateView):
    template_name = 'home.html'
