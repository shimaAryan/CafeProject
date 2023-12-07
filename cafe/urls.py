from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


app_name = 'cafe'
urlpatterns = [
    path('home', OrderItemView.as_view(), name='home'),
    path('cart', OrderItemView.as_view(), name='cart'),
]