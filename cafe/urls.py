from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'cafe'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('menu/', CategoryItems.as_view(), name='menu'),
    path('detail_item/<int:pk>', DetailItemView.as_view(), name='detail_item'),

    path('cart/', CartView.as_view(), name='cart'),
    path('cart-recipt/', ReceiptView.as_view(), name='receipt_list'),
]
