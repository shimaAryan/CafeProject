from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('staff_sign_up/', views.StaffSignUpView.as_view(), name='Staff_signup'),
    path('customer_sign_up/', views.CustomerSignUpView.as_view(), name='Customer_signup'),
    path('login/', views.UserLoginView.as_view(), name='User_login'),
    path('logout/', views.UserLogoutView.as_view(), name='User_logout'),
    path('index/', views.IndexView.as_view(), name='index'),
]
