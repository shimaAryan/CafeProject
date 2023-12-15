from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'cafe'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('menu/', CategoryItems.as_view(), name='menu'),
    path('detail_item/<int:pk>/', DetailItemView.as_view(), name='detail_item'),
    path('cart/', CartView.as_view(), name='cart'),
    path('index/', index,  name='index'),
    path('cart-receipt/<int:user_id>/', ReceiptView.as_view(), name='cart-receipt'),
    path('create_like/<int:pk>/', CreateLikeView.as_view(), name='create_like'),
    # path('delet_like', DeleteLikeView.as_view(), name='delet_like'),
    path('delet_like/<int:pk>/', DeleteLikeView.as_view(), name='delet_like'),

    


]