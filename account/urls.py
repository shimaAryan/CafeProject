from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('staff_sign_up/', views.StaffSignUpView.as_view(), name='Staff_signup'),
    path('customer_sign_up/', views.CustomerSignUpView.as_view(), name='Customer_signup'),
    path('login/', views.UserLoginView.as_view(), name='User_login'),
    path('logout/', views.UserLogoutView.as_view(), name='User_logout'),
    path('reset_pass/', views.UserPasswordResetView.as_view(), name='reset_password'),
    path('reset_done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('confirm/<uidb64>/<token>', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('confirm/complete', views.PasswordResetCompleteView.as_view(), name='password_reset_completed'),
    path('index/', views.IndexView.as_view(), name='index'),
]
