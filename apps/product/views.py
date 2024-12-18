from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView

from apps.product.models import Product, Category
from apps.user.models import Likes, AboutCart


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product/product-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        if self.request.user.is_authenticated:
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            liked_products = []
        context['liked_products'] = list(liked_products)
        context['cart_items_count'] = cart_items_count
        return context

    def post(self, request, *args, **kwargs):
        search = request.POST.get('search')
        if search:
            products = Product.objects.filter(
                Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search))
        else:
            products = Product.objects.all()
        context = self.get_context_data(object_list=products)
        context['products'] = products
        return render(request, self.template_name, context=context)


class ProductsByCategoryView(View):
    def get(self, request, slug):
        category = Category.objects.get(slug=slug)
        categories = Category.objects.all()
        products = Product.objects.filter(category=category)
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        if self.request.user.is_authenticated:
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            liked_products = []
        context = {
            'products': products,
            'active_category': category.name,
            'categories': categories,
            'liked_products': list(liked_products),
            'cart_items_count': cart_items_count
        }

        return render(request, 'product/product-list.html', context=context)

    def post(self, request, slug):
        category = Category.objects.get(slug=slug)
        categories = Category.objects.all()
        products = Product.objects.filter(category=category)
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        if self.request.user.is_authenticated:
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            liked_products = []
        context = {
            'products': products,
            'active_category': category.name,
            'categories': categories,
            'liked_products': list(liked_products),
            'cart_items_count': cart_items_count
        }
        return render(request, 'product/product-list.html', context=context)


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    template_name = 'product/product-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        if self.request.user.is_authenticated:
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            liked_products = []
        context['liked_products'] = list(liked_products)
        context['cart_items_count'] = cart_items_count
        return context


class LikedProductsListView(LoginRequiredMixin, ListView):
    template_name = 'product/liked-product-list.html'
    context_object_name = 'products'

    def get_queryset(self):
        liked_products_list = list(Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        products = Product.objects.filter(id__in=liked_products_list)
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        liked_products = list(Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart)
        context['liked_products'] = list(liked_products)
        context['cart_items_count'] = cart_items_count
        return context

    def post(self, request, *args, **kwargs):
        search = request.POST.get('search')
        user = request.user
        liked_products_list = Likes.objects.filter(user=user).values_list('product_id', flat=True)
        if search:
            products = Product.objects.filter(
                (Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search)) &
                Q(id__in=liked_products_list))
        else:
            products = Product.objects.all()
        context = self.get_context_data(object_list=products)
        context['products'] = products
        return render(request, self.template_name, context=context)
