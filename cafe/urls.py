from django.urls import path
from .views import *


app_name = 'cafe'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('menu/', CategoryItems.as_view(), name='menu'),
    path('detail_item/<int:pk>', DetailItemView.as_view(), name='detail_item'),
    path('cart/', CartView.as_view(), name='cart'),
    path('index/', index,  name='index'),
    path('cart-receipt/<int:user_id>', ReceiptView.as_view(), name='cart-receipt'),

]