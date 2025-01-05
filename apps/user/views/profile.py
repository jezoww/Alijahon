from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, UpdateView

from apps.user.forms import ProfileModelForm, ChangePasswordForm
from apps.user.models import Profile, Region, District


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'user/profile.html'
    form_class = ProfileModelForm
    pk_url_kwarg = 'pk'
    context_object_name = 'profile'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        obj, _ = Profile.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        return context

    def form_valid(self, form):
        district_id = self.request.POST.get('district')
        if district_id:
            form.instance.district = get_object_or_404(District, pk=district_id)
        messages.success(self.request, "Profile successfully updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)


class GetDistricts(LoginRequiredMixin, View):
    def get(self, request):
        region_name = request.GET.get('region')  # AJAX so‘rovdan viloyat nomini olish
        districts = District.objects.filter(region__name=region_name)  # Viloyatga tegishli tumanlar
        district_list = list(districts.values('id', 'name'))  # JSON uchun list yaratish
        return JsonResponse({'districts': district_list})


class ChangePasswordFormView(LoginRequiredMixin, FormView):
    template_name = 'user/profile.html'
    form_class = ChangePasswordForm

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.request.user.pk})

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data.get('password')
        if user.check_password(password):
            new_password = form.cleaned_data.get('new_password')
            user.password = make_password(new_password)
            user.save()
            login(self.request, user)
            messages.success(self.request, "Password successfully changed!")
        else:
            messages.error(self.request, 'Incorrect password!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)

        return super().form_invalid(form)
