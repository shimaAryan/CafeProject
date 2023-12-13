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

from django.http import JsonResponse

user = get_user_model()


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
    )


class CartView(View):
    template_name = "cart.html"
    context_object_name = "item_orders"
    model = Order

    def get(self, request, *args, **kwargs):
        context = {
            'item_data': request.session.get('order', 'No items in cart'),
            'order': None,
            'item_total': 0,
            'subtotal': 0,
            'total': 0,
            'discount_total': 0,
        }
        try:

            order_obj = Order.objects.get(user_order=request.user.id)
            print("99999999", order_obj)
            context['order'] = order_obj
            print("8888888888", context['order'])

            order_data = request.session.get('order', [])
            for order in order_data:
                quantity = order.get('quantity', 0)
                price = order.get('price', 0)
                discount = order.get('discount', 0)

                item_total = quantity * price - discount
                order['item_total'] = item_total
                context['discount_total'] += discount

                context['subtotal'] += order['item_total']
            context['total'] += context['subtotal'] + order_obj.delivery_cost
            context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))

        except Order.DoesNotExist:

            context['error'] = "Order does not exist"

            return render(request, self.template_name, context)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:

            new_order = json.loads(request.body)
            existing_orders = request.session.get('order', [])
            existing_orders.append(new_order)

            request.session['order'] = existing_orders

            request.session.modified = True
            print("------------------", existing_orders)
            return JsonResponse({'message': 'Order has been added successfully'})

        except JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON data in the request'}, status=400)
        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({'error': 'An error occurred while processing the request'},
                                status=500)

    # -----------------------------------------------------------------------


class ReceiptView(LoginRequiredMixin, SuccessMessageMixin, FormView, CartView):
    template_name = 'checkout.html'
    model = Receipt
    context_object_name = 'receipt'
    success_url = reverse_lazy("cafe:cart")
    form_class = receipt_form.PersonalInfo
    success_message = "Your information has been successfully registered"

    def setup(self, request, *args, **kwargs):
        self.user_id = get_object_or_404(user, id=kwargs["user_id"])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        user_pk = self.user_id
        if not user_pk == request.user.id:
            messages.error(request, "you must be logged in", "danger")
            return redirect("account:User_login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = CartView.get
        print("++++++++++++++++++++", order)
        if order:
            context.update({
                'form': self.form_class(),
            })
        else:
            raise Http404("No such order found")
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def form_valid(self, form):
        peyment = form.save(commit=False)
        for field_name, field_value in form.cleaned_data.items():
            self.request.session[field_name] = field_value
        messages.success(self.request, self.success_message, 'success')
        return super().form_valid(form)

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
