from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView

from apps.user.forms import RegisterModelForm, LoginForm
from apps.user.models import User, Cart, Profile


class RulesTemplateView(TemplateView):
    template_name = 'user/rules.html'


class RegisterCreateView(CreateView):
    template_name = 'user/register.html'
    model = User
    form_class = RegisterModelForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        if self.request.POST.get('rules') == 'true':
            user = form.save()
            Cart.objects.create(user=user)
            Profile.objects.create(user=user)
            messages.success(self.request, "Successfully registered!")
        else:
            messages.warning(self.request, 'You have to agree with our rules!')
            return redirect('register')
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)


class LoginFormView(FormView):
    template_name = 'user/login.html'
    success_url = reverse_lazy('index')
    form_class = LoginForm

    def form_valid(self, form):
        password = form.cleaned_data.get('password')
        phone = form.cleaned_data.get('phone')
        user = User.objects.get(phone=phone)
        if user.check_password(password):
            login(self.request, user)
            messages.success(self.request, "Successfully logged in!")
        else:
            messages.error(self.request, 'Incorrect password!')
            return redirect('login')
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect('login')