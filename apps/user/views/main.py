import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, FormView, UpdateView

from apps.product.models import Product, Category
from apps.user.forms import WithdrawModelForm
from apps.user.models import AboutCart, Withdraw
from apps.user.models import Likes
from apps.user.models import User, Competition


class IndexListView(ListView):
    context_object_name = 'products'
    template_name = 'index.html'
    paginate_by = 15

    def get_queryset(self):
        products = Product.objects.prefetch_related('images').select_related('category').all()
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            liked_products = []
            cart_items_count = 0
        context['liked_products'] = list(liked_products)
        context['cart_items_count'] = cart_items_count
        return context

    def post(self, request, *args, **kwargs):
        search = request.POST.get('search')
        if search:
            products = Product.objects.prefetch_related('images').select_related('category').filter(
                Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search))
        else:
            products = Product.objects.prefetch_related('images').select_related('category').all()
        context = self.get_context_data(object_list=products)
        context['products'] = products
        return render(request, self.template_name, context=context)


class LikeDislikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        product_id = data.get('product_id')
        is_liked = data.get('is_liked')

        product = Product.objects.get(id=product_id)
        user = request.user

        if is_liked:
            Likes.objects.get_or_create(user=user, product=product)
        else:
            Likes.objects.filter(user=user, product=product).delete()

        return JsonResponse({'status': 'success'})


class CompetitionListView(ListView):
    template_name = 'user/konkurs.html'
    context_object_name = 'users'

    def get_queryset(self):
        query = User.objects.all().annotate(total_sold=Sum('threads__sold', default=0)).order_by('-total_sold')
        return query

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        else:
            cart_items_count = 0
        if Competition.objects.exists():
            competition = Competition.objects.first()
        else:
            competition = "Soon"
        context['competition'] = competition
        context['cart_items_count'] = cart_items_count
        return context


class WithdrawFormView(LoginRequiredMixin, FormView):
    template_name = 'user/withdraw.html'
    form_class = WithdrawModelForm
    success_url = reverse_lazy('withdraw')

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        user = self.request.user
        if int(amount) > int(user.money):
            messages.error(self.request,
                           "Sizning hisobingizda mablag' yetarli emas. Iltimos, yetarlicha mablag' kirgizing!")
            return redirect('withdraw')
        withdraw = form.save(commit=False)
        withdraw.user = user
        user.money -= amount
        user.save()
        withdraw.save()
        messages.success(self.request, "Yuborildi!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['withdraw_history'] = self.request.user.withdraw_histories.all().order_by('-created_at')
        return context

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error[0])
        return super().form_invalid(form)
