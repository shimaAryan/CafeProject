from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


app_name = 'cafe'
urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart-recipt/', ReceiptView.as_view(), name='receipt_list'),
]