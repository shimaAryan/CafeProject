from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import Group
from django.contrib.auth import views as auth_view
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from core.models import Image
from .forms import CustomAuthenticationForm, StaffSignUpForm, UserRegisterForm
from .models import Staff, CustomUser


class StaffSignUpView(SuccessMessageMixin, CreateView):
    model = Staff
    template_name = 'account/staff_sign_up.html'
    success_url = reverse_lazy('cafe:index')
    form_class = StaffSignUpForm

    def form_valid(self, form):
        staff = form.save(commit=False)
        phonenumber = form.cleaned_data['phonenumber']
        try:
            user_register = CustomUser.objects.get(phonenumber=phonenumber)
            staff.user = user_register
            staff.save()
            Image.objects.create(image=form.cleaned_data['profile_image'],
                                 content_type=ContentType.objects.get_for_model(Staff),
                                 object_id=staff.id)
            messages.info(self.request, 'Cooperation Request: {} {} is registered'.format(user_register.firstname,
                                                                                          user_register.lastname))
            return super().form_valid(form)
        except CustomUser.DoesNotExist:
            return redirect(reverse('account:User_login'))


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
        group = Group.objects.get(name="customer")
        user.groups.add(group)
        messages.success(self.request, 'Account created successfully. You can now log in.')
        return super().form_valid(form)


class UserLoginView(auth_view.LoginView):
    template_name = 'account/login.html'
    success_url = reverse_lazy('account:index')
    form_class = CustomAuthenticationForm

    def form_valid(self, form) -> HttpResponse:
        super().form_valid(form)
        user = form.get_user()
        # Check if the user is an admin
        if user:
            return redirect(reverse('cafe:index'))
        else:
            return redirect(reverse('account:User_login'))

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid login credentials. Please try again.')
        return redirect(reverse('account:User_login'))


class IndexView(TemplateView):
    template_name = 'index.html'


class UserLogoutView(auth_view.LogoutView):
    next_page = reverse_lazy('account:index')


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


class StaffProfileView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Staff
    template_name = 'account/staff_profile.html'
    permission_required = 'Staff.view_staff'

    def get_queryset(self):
        queryset = Staff.objects.select_related('CustomUser').select_related('Image')
        return queryset

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     User = CustomUser.objects.all()
    #     staff_members = Staff.objects.all()
    #     profile_images = Image.objects.get(content_type=ContentType.objects.get_for_model(Staff), )
    #     context = {'profile_images': profile_images,
    #                'User': User,
    #                'staff_members': staff_members
    #                }
    #     return context
