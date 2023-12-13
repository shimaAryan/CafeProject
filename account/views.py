from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import Group
from django.contrib.auth import views as auth_view
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView
from .forms import CustomAuthenticationForm, StaffSignUpForm, UserRegisterForm
from .models import Staff, CustomUser


class StaffSignUpView(CreateView):
    model = Staff
    template_name = 'account/staff_sign_up.html'
    success_url = reverse_lazy('account:User_login')
    form_class = StaffSignUpForm

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        # Add the Staff user to a group
        group, created = Group.objects.get_or_create(name="staff")
        user.groups.add(group)
        messages.success(self.request, 'Account created successfully. You can now log in.')
        return super().form_valid(form)


class CustomerSignUpView(CreateView):
    model = CustomUser
    template_name = 'account/customer_sign_up.html'
    success_url = reverse_lazy('account:User_login')
    form_class = UserRegisterForm

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        # Add the Staff user to a group
        group, created = Group.objects.get_or_create(name="Customer")
        user.groups.add(group)
        return super().form_valid(form)


class UserLoginView(auth_view.LoginView):
    template_name = 'account/login.html'
    success_url = reverse_lazy('cafe:home')
    form_class = CustomAuthenticationForm

    def form_valid(self, form) -> HttpResponse:
        super().form_valid(form)
        user = form.get_user()
        # Check if the user is an admin
        if user.is_admin:
            return redirect(reverse('admin:index'))
        elif user.is_customer:
            return redirect(reverse('account:index'))
        elif user.is_staff:
            return redirect(reverse('cafe:home'))
        else:
            return redirect(reverse('account:User_login'))

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid login credentials. Please try again.')
        return redirect(reverse('account:User_login'))


class IndexView(TemplateView):
    template_name = 'index.html'


class UserLogoutView(auth_view.LogoutView):
    next_page = reverse_lazy('cafe:home')


class UserPasswordResetView(auth_view.PasswordResetView):
    template_name = 'account/password_resetform.html'
    success_url = reverse_lazy('account:password_reset_done')
    email_template_name = "account/password_reset_email.html"


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_completed')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'
