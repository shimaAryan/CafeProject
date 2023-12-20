from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('staff_sign_up/', views.StaffSignUpView.as_view(), name='Staff_signup'),
    path('customer_sign_up/', views.CustomerSignUpView.as_view(), name='Customer_signup'),
    path('login/', views.UserLoginView.as_view(), name='User_login'),
    path('logout/', views.UserLogoutView.as_view(), name='User_logout'),
    path('staff_profile/<int:user_id>', views.StaffProfileView.as_view(), name='Staff_profile'),
    path('user_profile/<int:user_id>', views.CustomUserProfileView.as_view(), name='user_profile'),
    path('update_profile/<int:user_id>', views.CustomerProfileUpdateView.as_view(), name='update_profile'),
    path('Staff_update_profile/<int:user_id>', views.StaffProfileUpdateView.as_view(), name='Staff_update_profile'),
    path('reset_pass/', views.UserPasswordResetView.as_view(), name='reset_password'),
    path('reset_done/', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('confirm/<uidb64>/<token>', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('confirm/complete', views.UserPasswordResetCompleteView.as_view(), name='password_reset_completed'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),
]
