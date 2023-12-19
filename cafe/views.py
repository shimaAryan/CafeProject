import json
from json import JSONDecodeError
from typing import Any
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, Http404, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from psycopg2 import OperationalError
from django.views.generic import ListView, View, DetailView, CreateView, TemplateView, DeleteView, FormView
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from core.models import Image, Comment
from .forms import search_form, receipt_form, detail_view_form
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from .models import *
from django.http import JsonResponse
from taggit.models import Tag
from django.template.loader import render_to_string

user = get_user_model()


class ContextMixin(LoginRequiredMixin):
    def get_context(self, user, session_data):
        context = {}
        if not user or not user.is_authenticated:
            messages.error(user, "You must have an account and be logged in", "danger")
            return redirect("account:User_login")
        else:
            try:
                order, created = Order.objects.get_or_create(user=user)

                order_items = OrderItem.objects.filter(order=order)

                if order.status == "ORDER":
                    context = {
                        'item_data': session_data,
                        'order': order,
                        'user_id': user.id,
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
        # print("*_" * 30, context)
        return context

    @staticmethod
    def item_search(request):
        items = Items.objects.all()
        form = search_form.SearchForm()
        if "search" in request.GET:
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
        item_ids = [item['id'] for item in session_order]
        similarity_item = self.get_similar_data(item_ids[0])
        context = self.get_context(request.user, session_order) if session_order else {
            'error': "Order does not exist"}
        context['similarity_item'] = similarity_item

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

class ReceiptView(ContextMixin, FormView):
    template_name = 'checkout.html'
    form_class = receipt_form.PersonalInfo
    success_url = reverse_lazy("cafe:cart")
    success_message = "Your information has been successfully registered"

    def dispatch(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        self.user1 = get_object_or_404(user, id=user_id)
        if not self.user1 == request.user:
            messages.error(request, "You must be logged in", "danger")
            return redirect("account:User_login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        payment = form.save(commit=False)
        for field_name, field_value in form.cleaned_data.items():
            self.request.session[field_name] = field_value
        messages.success(self.request, self.success_message, 'success')
        return super().form_valid(form)

    def get(self, request, **kwargs):
        context = self.get_context(self.user1, self.request.session.get('order', []))
        search = self.item_search(request)
        category_item_counts = CategoryMenu.objects.annotate(item_count=Count('items'))
        print("888", category_item_counts)

        all_tag = Tag.objects.values_list('name', flat=True).distinct()

        if not context:
            raise Http404("No such order found")

        context.update({
            'all_tag': all_tag,
            "search": search,
            "form": self.form_class,
            "category_item_counts": category_item_counts,
        })
        print("!!!!!!!!!", context)
        return render(request, self.template_name, context)


class ItemByTag(ListView):
    template_name = "tag_items.html"
    model = Items

    def get_context_data(self, *, tag_slug=None, **kwargs):
        super().get_context_data(**kwargs)
        tag = None
        select_item = Items.objects.all()
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            select_item = Items.objects.filter(tags__in=[tag])

        context = {
            'select_item': select_item,
            'tags': tag,
        }
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


class CommentListViewMixin(ListView):
    model = Comment
    context_object_name = 'commenttt'  # Set the context variable name for the comment list in the template
    paginate_by = 4  # Set the number of comments per page


class DetailItemView(LoginRequiredMixin, CreateView, CommentListViewMixin):
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
        context["likes_count"] = Like.objects.filter(items=item_obj.id, user=self.request.user).count()

        
        return context

    def form_valid(self, form: BaseModelForm):
        self.object = form.save(commit=False)
        self.object.content_type = ContentType.objects.get_for_model(Items)
        self.object.object_id = self.kwargs["pk"]
        self.object.user = self.request.user
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


def index(request):
    return render(request, 'index.html')


class HomeView(TemplateView):
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
