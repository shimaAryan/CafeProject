from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('sign_up/', views.StaffSignUpView.as_view(), name='User_signup'),
    path('login/', views.UserLoginView.as_view(), name='User_login'),
    path('logout/', views.UserLogoutView.as_view(), name='User_logout'),
    path('index/', views.IndexView.as_view(), name='index'),
]
