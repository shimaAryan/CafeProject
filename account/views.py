from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView
from .forms import CustomAuthenticationForm, UserRegisterForm
from .models import Staff, CustomUser


class StaffSignUpView(CreateView):
    model = Staff
    template_name = 'account/staff_sign_up.html'
    success_url = reverse_lazy('account:User_login')
    fields = ("phonenumber", "email", "firstname", "lastname", "password", "nationalcode", "date_of_birth",
              "experience", "rezome", "profile_image", "guarantee", "how_know_us")

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        # Add the Staff user to a group
        group, created = Group.objects.get_or_create(name="staff")
        user.groups.add(group)
        return super().form_valid(form)


class CustomerSignUpView(CreateView):
    model = CustomUser
    template_name = 'account/customer_sign_up.html'
    success_url = reverse_lazy('account:User_login')
    fields = ("phonenumber", "email", "firstname", "lastname", "password", "how_know_us")


    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        # Add the Staff user to a group
        group, created = Group.objects.get_or_create(name="Customer")
        user.groups.add(group)
        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = 'account/login.html'
    success_url = reverse_lazy('cafe:home')
    form_class = CustomAuthenticationForm

    def form_valid(self, form) -> HttpResponse:
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
        print("5" * 35)
        return redirect(reverse('account:User_signup'))


class IndexView(TemplateView):
    template_name = 'index.html'


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('cafe:home')
