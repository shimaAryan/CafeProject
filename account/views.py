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
from django.views.generic import TemplateView, CreateView, ListView, UpdateView
from core.models import Image, Comment
from .forms import CustomAuthenticationForm, StaffSignUpForm, UserRegisterForm, CommentToManagerForm, \
    UserProfileUpdateForm, StaffUpdateForm
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

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('cafe:index')
        return super().dispatch(request, *args, **kwargs)

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


class StaffProfileView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Staff
    template_name = 'account/staff_profile.html'
    permission_required = 'Staff.view_staff'

    def __init__(self):
        super().__init__()
        self.object_list = None

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            context = self.get_context_data()
            context['error_message'] = "You don't have access to this part of the page."
            return self.render_to_response(context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Staff.objects.select_related('user')
        return queryset

    def get_context_data(self, object_list=None, **kwargs):
        super().get_context_data(**kwargs)
        profile_images = Image.objects.filter(content_type=ContentType.objects.get_for_model(Staff))
        self.object_list = self.get_queryset()
        context = {
            "Images": profile_images,
            "object_list": self.object_list,
        }
        return context


class CustomUserProfileView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'account/customuser_profile.html'

    def dispatch(self, request, *args, **kwargs):
        if Staff.objects.filter(user=request.user.id).exists() and request.user.is_customer:
            messages.warning(
                self.request,
                'Management is reviewing your cooperation request. Thank you for joining our members.'
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CustomUser.objects.filter(id=self.request.user.id)
        return queryset

    def get_context_data(self, object_list=None, **kwargs):
        super().get_context_data(**kwargs)
        form = CommentToManagerForm
        context = {
            "form": form,
            "Customuser_profile": self.get_queryset(),
        }
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = CommentToManagerForm(request.POST)
            if form.is_valid():
                datas = form.cleaned_data
                new_comment = Comment.objects.create(
                    content=datas["content"],
                    content_type=ContentType.objects.get_for_model(CustomUser),
                    object_id=request.user.id,
                    user=request.user,
                )
                messages.success(request, 'Comment added successfully.')
                return redirect(reverse('cafe:index'))
        return self.get(request, *args, **kwargs)


class CustomerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileUpdateForm
    template_name = 'account/customer_profile_update.html'
    success_url = reverse_lazy('cafe:index')

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class StaffProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Staff
    form_class = StaffUpdateForm
    template_name = 'account/Staff_profile_update.html'

    def get_object(self, queryset=None):
        user = self.request.user
        staff = Staff.objects.get(user=user)
        return staff

    def get_success_url(self):
        # Redirect to the 'Staff_update_profile' page with the updated user's ID
        return reverse('account:Staff_profile', kwargs={'user_id': self.request.user.id})


class AboutUsView(TemplateView):
    template_name = 'about.html'
