from django.shortcuts import render
import json
from json import JSONDecodeError
from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, Http404, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from psycopg2 import OperationalError
from django.views.generic import ListView, View, CreateView, TemplateView, FormView, UpdateView
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from core.models import Image, Comment
from .forms import search_form, receipt_form, detail_view_form
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from .models import *
from django.http import JsonResponse
from taggit.models import Tag

user = get_user_model()


class ContextMixin():
    def get_context(self, session_data):
        context = {}

        try:

            context = {
                'item_data': session_data,
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
                item_total = int(quantity) * price - discount
                item['item_total'] = item_total
                context['discount_total'] += discount
                context['subtotal'] += item_total
                context['delivery_cost'] = item_total * 2
            context['total'] = context['subtotal'] + context['delivery_cost']


        except OrderItem.DoesNotExist:
            context['error'] = "Order Items does not exist"
        except Order.DoesNotExist:
            context['error'] = "Order does not exist"

        return context

    @staticmethod
    def item_search(request):
        items = Items.objects.none()
        form = search_form.SearchForm()
        if "search" in request.GET:
            items = Items.objects.all()
            form = search_form.SearchForm(request.GET)
            if form.is_valid():
                try:
                    cd = form.cleaned_data["search"]
                    items = (items.annotate(similarity=Greatest(
                        TrigramSimilarity("title", cd),
                        TrigramSimilarity("description", cd), ))
                             .filter(similarity__gt=0.1).order_by("-similarity"))
                except OperationalError:
                    messages.error("operational error", "danger")
                    items = []

        context = {
            "search_form": form,
            "items": items

        }
        return context


class SimilarityItemMixin:
    def get_similar_data(self, item_id):
        current_item = get_object_or_404(Items, id=item_id)
        item_tags_ids = current_item.tags.values_list('id', flat=True)
        similar_item = Items.objects.filter(tags__in=item_tags_ids).exclude(id=item_id)
        similar_item = similar_item.annotate(same_tags=Count('tags')).order_by('-same_tags', '-price')[:4]
        context = {
            'item': current_item,
            'similar_item': similar_item,
        }
        return context


class CartView(ContextMixin, SimilarityItemMixin, View):
    template_name = "cart.html"

    def get(self, request, *args, **kwargs):

        session_order = request.session.get('order', [])

        self.context = self.get_context(session_order) if session_order else {
            'error': "Order does not exist"}
        item_ids = [item['id'] for item in session_order]

        self.context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))
        if item_ids:
            self.similarity_item = self.get_similar_data(item_ids[0])
            self.context['similarity_item'] = self.similarity_item
        return render(request, self.template_name, self.context)

    @staticmethod
    def post(request, *args, **kwargs):
        try:

            new_order = json.loads(request.body)
            session_order = request.session.get('order', [])
            list_id = [item.get("id") for item in session_order]

            is_exist = False

            for item in session_order:
                if item['id'] == new_order['id']:
                    is_exist = True

                    item['quantity'] = int(item['quantity']) + int(new_order['quantity'])
                    break
            if not is_exist:
                session_order.append(new_order)
            request.session['order'] = session_order
            request.session.modified = True
            return JsonResponse({'message': 'Order has been added successfully'})
        except JSONDecodeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ReceiptView(LoginRequiredMixin, UpdateView, ContextMixin):
    model = user
    template_name = 'checkout.html'
    form_class = receipt_form.PersonalInfo
    success_url = reverse_lazy("cafe:cart-receipt", args={"status": "payment"})
    success_message = "Your information has been successfully registered"

    # def get_success_url(self):
    #     return reverse("cafe:cart-receipt", kwargs={'status': "payment"})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in", "danger")
            return redirect("account:User_login")

        self.user_id = self.request.user.id
        order, created = Order.objects.get_or_create(user_id=self.user_id)
        order.status = "payment"
        order.save()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, query_set=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_order = self.request.session.get('order', [])
        context.update({
            'session_data': self.get_context(session_order) if session_order else
            {'error': "Order does not exist"},
            'all_tag': Tag.objects.values_list('name', flat=True).distinct(),
            "search": self.item_search(self.request),
            "category_item_counts": CategoryMenu.objects.annotate(item_count=Count('items')),
            'delivery_form': receipt_form.DeliveryTime
        })

        return context


class PaymentView(LoginRequiredMixin, ContextMixin, CreateView):
    template_name = "payment_done.html"
    model = Receipt
    form_class = receipt_form.DeliveryTime

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in", "danger")
            return redirect("account:User_login")
        self.user_id = request.user.id
        self.order_instance = get_object_or_404(Order, user_id=self.user_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        session_order = request.session.get('order', [])
        context = self.get_context(session_order) if session_order else {
            'error': "Order does not exist"}

        OrderItem.objects.filter(order=self.order_instance).delete()

        for item in session_order:
            order_item = OrderItem(order=self.order_instance)
            order_item.quantity = item.get("quantity", 1)
            order_item.delivery_cost = item.get("delivery_cost", 0)
            order_item.save()

            item_id = item.get('id', [])
            item_instance = Items.objects.get(id=item_id)
            order_item.items.add(item_instance)
            order_item.save()

        # del self.request.session['order']
        sessionStorage.clear()


        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        delivery_time_form = receipt_form.DeliveryTime(request.POST)
        if delivery_time_form.is_valid():
            cd = delivery_time_form.cleaned_data.items()

            delivery_time = delivery_time_form.save(commit=False)
            order_item = Order.objects.create(status="paid")
            order_item.delivery_times.add(delivery_time)
            return render(request, self.template_name)
        return redirect(request, "cafe:payment_paid' 'paid")



class FilterCategory(ListView):
    template_name = "cat_item.html"
    context_object_name = 'cat_item'
    model = Items

    def get_queryset(self):
        self.category_name = self.kwargs['cat_name']
        queryset = Items.objects.filter(category_id__title=self.category_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_name'] = self.category_name
        context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))
        return context


class ItemByTag(ListView):
    template_name = "tag_items.html"
    model = Items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = None
        select_item = Items.objects.all()
        if tag_slug := self.kwargs.get('tag_slug'):
            tag = get_object_or_404(Tag, slug=tag_slug)
            select_item = Items.objects.filter(tags__in=[tag])

        context = {
            'images' : Image.objects.filter(content_type=ContentType.objects.get_for_model(Items)),
            'select_item': select_item,
            'tags': tag,
        }
        return context


class DeleteCartItemView(View):
    template_name = "cart.html"

    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        is_exist = False
        session_order_item = self.request.session.get('order', [])
        print(session_order_item)
        for item in session_order_item:
            print(item_id), item['id']
            if int(item['id']) == int(item_id):
                is_exist = True
                if int(item['quantity']) > 1:
                    item['quantity'] = int(item['quantity']) - 1
                    self.request.session.modified = True
                else:
                    print(self.request.session["order"])
                    del self.request.session["order"]["item_data"][item["id"]]
                    request.session.modified = True

                break

        if not is_exist:
            return JsonResponse({'message': 'Item does not exist in cart.', "quantity": item['quantity']})
        return JsonResponse({'message': 'Item removed successfully.', "quantity": item['quantity']})


class CategoryItems(ListView):
    model = CategoryMenu
    context_object_name = "categorys"
    template_name = 'menu1.html'

    def get_queryset(self):
        return self.model.objects.prefetch_related("items").all()

    def get_context_data(self, *, category_id=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.request.GET.get('category_id')
        items_category = None

        if category_id:
            items_category = Items.objects.filter(category_id=category_id)
        context['items_category'] = items_category
        context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))

        return context


class CommentListViewMixin(ListView):
    model = Comment
    context_object_name = 'commenttt'
    paginate_by = 4


class DetailItemView(CreateView, CommentListViewMixin):
    model = Comment
    context_object_name = "comment"
    template_name = "detail_item.html"
    form_class = detail_view_form.CommentForm

    def get_success_url(self):
        messages.success(self.request, 'Comment created successfully!')
        return reverse('cafe:detail_item', kwargs={'pk': self.kwargs["pk"]})

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        item_obj = Items.objects.get(id=self.kwargs["pk"])

        context["item"] = item_obj
        context["image"] = Image.objects.get(object_id=self.kwargs.get('pk'),
                                             content_type=ContentType.objects.get_for_model(Items))
        if Like.is_liked(self.request.user, item_obj):
            context["like_status"] = "True"
        else:
            context["like_status"] = False
        context["likes_count"] = Like.objects.filter(items=item_obj.id).count()

        return context

    def form_valid(self, form: BaseModelForm):
        self.object = form.save(commit=False)
        self.object.content_type = ContentType.objects.get_for_model(Items)
        self.object.object_id = self.kwargs["pk"]
        # self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class CreateLikeView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "not_autenticate"}, status=401)

        item_obj = Items.objects.get(id=pk)
        like_count = Like.objects.filter(items=item_obj).count()

        like_obj = Like.objects.get_or_create(items=item_obj, user=request.user)
        if like_obj[1] == True:
            like_obj[0].save()
            return JsonResponse({"liked_status": True, "like_count": like_count})


class LikeStatus(View):
    def get(self, request, pk):
        item_obj = Items.objects.get(id=pk)
        like_count = Like.objects.filter(items=item_obj).count()

        if Like.is_liked(self.request.user, item_obj):
            return JsonResponse({"liked_status": True, "like_count": like_count})
        else:
            return JsonResponse({"liked_status": False, "like_count": like_count})


class DeleteLikeView(View):

    def get(self, request, pk):
        if not request.user.is_authenticated:
            item_obj = Items.objects.get(id=pk)
            like_count = Like.objects.filter(items=item_obj).count()
            return JsonResponse({"detail": "login_error"}, status=401)

        item_obj = Items.objects.get(id=pk)
        # print(request)

        like_obj = Like.objects.filter(items=item_obj, user=request.user).first()
        if like_obj:
            like_obj.delete()

        like_count = Like.objects.filter(items=item_obj).count()
        return JsonResponse({"liked_status": False, "like_count": like_count})


class IndexView(TemplateView):
    template_name = 'index.html'


class BestItemsView(TemplateView):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        list_category = CategoryMenu.objects.all()
        best_items = {}
        for category in list_category:
            best_items[category] = Items.best_items(category.id)
        context["best_items"] = best_items
        context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))

        return context

    template_name = "best_items.html"

