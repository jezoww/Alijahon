from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView

from apps.product.models import Product, Category, ProductImage
from apps.user.models import Likes, AboutCart


class ProductListView(ListView):
    context_object_name = 'products'
    template_name = 'product/product-list.html'
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
            products = Product.objects.prefetch_related('images').prefetch_related('category').all()
        context = self.get_context_data(object_list=products)
        context['products'] = products
        return render(request, self.template_name, context=context)


class ProductsByCategoryView(View):
    def get(self, request, slug):
        category = Category.objects.prefetch_related('products').get(slug=slug)
        categories = Category.objects.all()
        products = category.products.prefetch_related('images').all()
        paginator = Paginator(products, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            cart_items_count = 0
            liked_products = []
        context = {
            'products': page_obj.object_list,
            'active_category': category.name,
            'categories': categories,
            'liked_products': list(liked_products),
            'cart_items_count': cart_items_count,
            'page_obj': page_obj,
        }

        return render(request, 'product/product-list.html', context=context)

    def post(self, request, slug):
        search = request.POST.get("search", None)
        category = Category.objects.get(slug=slug)
        categories = Category.objects.all()
        products = Product.objects.prefetch_related('images').prefetch_related('category').filter(
            category=category)
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search))
        paginator = Paginator(products, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            cart_items_count = 0
            liked_products = []
        context = {
            'products': page_obj.object_list,
            'active_category': category.name,
            'categories': categories,
            'liked_products': list(liked_products),
            'cart_items_count': cart_items_count,
            'page_obj': page_obj,
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
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
            liked_products = Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        else:
            cart_items_count = 0
            liked_products = []
        context['liked_products'] = list(liked_products)
        context['cart_items_count'] = cart_items_count
        return context


class LikedProductsListView(LoginRequiredMixin, ListView):
    template_name = 'product/liked-product-list.html'
    context_object_name = 'products'
    paginate_by = 15

    def get_queryset(self):
        liked_products_list = list(Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        products = Product.objects.prefetch_related('images').prefetch_related('category').filter(
            id__in=liked_products_list)
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        liked_products = list(Likes.objects.filter(user=self.request.user).values_list('product_id', flat=True))
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        else:
            cart_items_count = 0
        context['liked_products'] = list(liked_products)
        context['cart_items_count'] = cart_items_count
        return context

    def post(self, request, *args, **kwargs):
        search = request.POST.get('search')
        user = request.user
        liked_products_list = Likes.objects.filter(user=user).values_list('product_id', flat=True)
        if search:
            products = Product.objects.prefetch_related('images').prefetch_related('category').filter(
                (Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search)) &
                Q(id__in=liked_products_list))
        else:
            products = Product.objects.prefetch_related('images').prefetch_related('category').all()
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        else:
            cart_items_count = 0
        context = self.get_context_data(object_list=products)
        context['cart_items_count'] = cart_items_count
        context['products'] = products
        return render(request, self.template_name, context=context)
