from django.urls import path
from .views import *


app_name = 'cafe'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('menu/', CategoryItems.as_view(), name='menu'),
    path('detail_item/<int:pk>/', DetailItemView.as_view(), name='detail_item'),

    path('cart/', CartView.as_view(), name='cart'),
    path('cart-receipt/<str:status>/', ReceiptView.as_view(), name='cart-receipt'),
    path('payment/<str:status>/', PaymentView.as_view(), name='payment_paid'),
    path('item-tag/<slug:tag_slug>/', ItemByTag.as_view(), name="items_by_tag"),
    path('item-category/<str:cat_name>/', FilterCategory.as_view(), name="cat_item"),
    path('delete-item-from-cart/', DeleteCartItemView.as_view(), name='delete_item_from_cart'),
    path('create_like/<int:pk>/', CreateLikeView.as_view(), name='create_like'),
    path('delet_like/<int:pk>/', DeleteLikeView.as_view(), name='delet_like'),
    path('best_items/', BestItemsView.as_view(), name='best_items'),
    path('json_check_like/<int:pk>/', LikeStatus.as_view(), name='check_like')

]
