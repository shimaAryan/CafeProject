from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import UserLoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView


class UserLoginView(View):
    form_login = UserLoginForm
    template_name = 'account/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_login()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        log = self.form_login(request.POST)
        if log.is_valid():
            datas = log.cleaned_data
            user = authenticate(request, username=datas["nationalcode"], password=datas["password"])
            if user is not None:
                login(request, user)
                return redirect("cafe:home")
        messages.warning(request,
                         f"Please enter correct phone number or email and password or Please"
                         f" register in Ada company site first before login",
                         "warning")
        return self.get(request)


class IndexView(TemplateView):
    template_name = 'index.html'
