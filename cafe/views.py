import json
from json import JSONDecodeError
from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, Http404, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from psycopg2 import OperationalError
from django.views.generic import ListView, View, CreateView, TemplateView, FormView
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
    # def get_context(self, user, session_data):
    def get_context(self, session_data,user=None):
        context = {}

        # if not user or not user.is_authenticated:
        #     messages.error(user, "You must have an account and be logged in", "danger")
        #     return redirect("account:User_login")
        # else:
        try:
            # order, created = Order.objects.get_or_create(user=user)
            # if order.status == "order":
            context = {
                'item_data': session_data,
                # 'user_id': user.id,
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
        # else:
        #     return HttpResponse("you dont have any order items in your cart ")
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
        print("request data=================", self.request)
        session_order = request.session.get('order', [])

        self.context = self.get_context(session_order) if session_order else {
            'error': "Order does not exist"}
        item_ids = [item['id'] for item in session_order]
        if item_ids:
            self.similarity_item = self.get_similar_data(item_ids[0])
            self.context['similarity_item'] = self.similarity_item

        return render(request, self.template_name, self.context)

    @staticmethod
    def post(request, *args, **kwargs):
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

class ReceiptView(LoginRequiredMixin, ContextMixin, FormView):
    template_name = 'checkout.html'
    form_class = receipt_form.PersonalInfo
    context_object_name = "receipt"
    success_message = "Your information has been successfully registered"

    def get_success_url(self):
        return reverse("cafe:cart-receipt", kwargs={'status': "payment"})

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == "AnonymousUser":
            messages.error(request, "You must be logged in", "danger")
            return redirect("account:User_login")
        self.user_id = request.user.id
        order, created = Order.objects.get_or_create(user_id=self.user_id)
        order.status = "payment"
        order.save()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        print("im hereeeeeeee")
        user_info = form.save(commit=False)
        user_info.save()
        messages.success(self.request, self.success_message, 'success')
        return super().form_valid(form)

    def form_invalid(self, form):
        print("im noww here")
        messages.error(self.request, "Invalid form data", 'danger')
        context = self.get_context_data(form=form, form_errors=form.errors)
        print("------", context)
        return self.render_to_response(context)

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
        print("!!!!!!!!!", context)
        return context


class PaymentView(LoginRequiredMixin, ContextMixin, CreateView):
    template_name = "payment_done.html"


    def dispatch(self, request, *args, **kwargs):
        if self.request.user == "AnonymousUser":
            messages.error(request, "You must be logged in", "danger")
            return redirect("account:User_login")
        self.user_id = request.user.id
        self.order_instance = get_object_or_404(Order, user_id=self.user_id)
        return super().dispatch(request, *args, **kwargs)

    # def form_valid(self, form):
    #     print("^^^^^^^^^^^^")
    #     delivery_time = form.save(commit=False)  # Saving the form data for DeliveryTime
    #     receipt = Receipt(order=self.order_instance, delivery_time=delivery_time)  # Creating a Receipt object
    #     receipt.save()  # Saving the Receipt object to the database
    #     self.order_instance.status = "paid"  # Updating the order status
    #     self.order_instance.save()  # Saving the updated order status
    #     messages.success(self.request, "Payment successful")  # Notifying the user about the successful payment
    #     return super().form_valid(form)

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

        return super().get(request, *args, **kwargs)
        # return render(request, self.template_name)

        # order_item_fields = [field.name for field in OrderItem._meta.get_fields()]
        # print(">>>>>>>>>>>>>>",  order_item_fields)
        # session_item = {key: value for key, value in request.session.items() if key in order_item_fields}
        # new_item =OrderItem(**session_item)

        # print("newwwwww",new_item)
        # new_item.save()


        # return HttpResponse("done")


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
            'select_item': select_item,
            'tags': tag,
        }
        print("----------", context)
        return context


# class ItemSearchView(ListView):
#     model = Items
#     template_name = 'checkout.html'
#     context_object_name = 'items'
#     form_class = search_form.SearchForm
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         search_query = self.request.GET.get('search', None)
#         if search_query:
#             queryset = queryset.annotate(similarity=Greatest(
#                 TrigramSimilarity("title", search_query),
#                 TrigramSimilarity("description", search_query)))
#             queryset = queryset.filter(similarity__gt=0.1).order_by('-similarity')
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['search_form'] = self.get_form()
#         print("kkkkkkkkkkk",context)
#         return context

# def get_form(self):
#     form = self.form_class()
#     if 'search' in self.request.GET:
#         form = self.form_class(self.request.GET)
#     return form


# class CreateItem(LoginRequiredMixin,FormView):
#     form_class = create_post.CreateItem
#     template_name = "item_create.html"
#     success_url = reverse_lazy("cafe:menu")
#
#     def get_context_data(self, **kwargs):
#         user = Items.objects.select_related(Order)
#     def form_valid(self, form):
#         super().form_valid(self, form)
#         new_item = form.save(commit=False)
#         post.author = request.user
#         new_item.save()
#         form.save_m2m()

class DeleteCartItemView(View):
    template_name = "cart.html"

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            item_id = request.POST.get('item_id')
            session_order_item = self.request.session.get('order', [])
            order_item_ids = [item['id'] for item in session_order_item]
            if item_id in order_item_ids:
                del session_order_item['item_data'][item_id]
                request.session.modified = True
                return JsonResponse({'message': 'Item deleted from the cart.'})
        return JsonResponse({'error': 'An error occurred while deleting the item from the cart.'}, status=400)


class CategoryItems(ListView, ):
    model = CategoryMenu
    context_object_name = "categorys"
    template_name = 'menu1.html'

    def get_queryset(self):
        return self.model.objects.prefetch_related("items").all()

    def get_context_data(self, *, category_id=None, **kwargs):
        print("request data=================", self.request.user.id)
        context = super().get_context_data(**kwargs)
        category_id = self.request.GET.get('category_id')
        items_category = None

        if category_id:
            items_category = Items.objects.filter(category_id=category_id)
        print("'''''''''''''''", context)
        context['items_category'] = items_category
        context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))

        return context


class CommentListViewMixin(ListView):
    model = Comment
    context_object_name = 'commenttt'  # Set the context variable name for the comment list in the template
    paginate_by = 4  # Set the number of comments per page


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
        # context["likes_count"] = Like.objects.filter(items=item_obj.id, user=self.request.user).count()

        
        return context

    def form_valid(self, form: BaseModelForm):
        self.object = form.save(commit=False)
        self.object.content_type = ContentType.objects.get_for_model(Items)
        self.object.object_id = self.kwargs["pk"]
        # self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class LikeStatus(View):
        def get(self,request,pk):
            item_obj=Items.objects.get(id=pk)
            like_count=Like.objects.filter(items=item_obj).count()
            
            if Like.is_liked(self.request.user,item_obj):
                return JsonResponse({"liked_status":True,"like_count":like_count})
            else:
                return JsonResponse({"liked_status":False,"like_count":like_count})

class CreateLikeView(View):

    def get(self, request, pk):
        item_obj = Items.objects.get(id=pk)
        print(request)
        like_obj = Like.objects.get_or_create(items=item_obj, user=request.user)
        if like_obj[1] == True:
            like_obj[0].save()
        like_count=Like.objects.filter(items=item_obj).count()
       
        # html_like=render_to_string  ("partial/like.html",{'item':like_obj})
        return JsonResponse({"liked_status":True,"like_count":like_count})

        # messages.success(request, 'thanks!')
        # html_like = render_to_string("partial/like.html", {'item': like_obj})
        # return JsonResponse({"like_html": html_like})

        # return redirect(reverse('cafe:detail_item', kwargs={"pk":pk}))


class DeleteLikeView(View):
    def get(self, request, pk):
        item_obj = Items.objects.get(id=pk)
        print(request)

        like_obj=Like.objects.filter(items=item_obj,user=request.user).first()
        if like_obj:
            like_obj.delete()
       
        like_count=Like.objects.filter(items=item_obj).count()
        return JsonResponse({"liked_status":False,"like_count":like_count})

    # def handle_no_permission(self):
    #      return render(request, 'unauthorized_access.html', {})

    # def get_object(self, queryset=None):
    #     idd = self.kwargs.get('pk')

    #     return Items.objects.get(id=idd)

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["image"] = Image.objects.get(object_id=self.kwargs.get('pk'))
    #     return context

class IndexView(TemplateView):
    template_name = 'index.html'

# class CreateCommentView(CreateView):
#     model = Comment
#     fields = ['content']
#     template_name = "detail_item.html"
#     success_message = "Your comment was sent successfully"
#     success_url = reverse_lazy('cafe:detail_item')

#     def form_valid(self, form):
#         print("list_categoryoooooooooooooooooooooooooooooooooooo")
#         comment = form.save(commit=False)
#         # You can perform additional operations on the comment object here if needed
#         print("ss"*10,self)
#         comment.save()
#         return list_category
    
#     # def get_success_message(self, cleaned_data):
#     #     return self.success_message
    
class BestItemsView(TemplateView):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context=super().get_context_data(**kwargs)
        list_category=CategoryMenu.objects.all()
        best_items={}
        for category in list_category:
            best_items[category]=Items.best_items(category.id)
        context["best_items"]=best_items
        context["images"] = Image.objects.filter(content_type=ContentType.objects.get_for_model(Items))
        
        # print("////////////////////////////////////////////////////////",context)
        return context
    template_name="best_items.html"
       
#         return super().form_valid(form)

#     # def get_success_message(self, cleaned_data):
#     #     return self.success_message
