import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Value, IntegerField, F
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, FormView, ListView, UpdateView, DeleteView, DetailView

from apps.product.models import Product, Category
from apps.user.forms import RegisterModelForm, LoginForm, ProfileModelForm, ChangePasswordForm, ThreadModelForm
from apps.user.models import User, Likes, Cart, Profile, Region, District, AboutCart, Order, AboutOrder, Seller, Thread


class IndexListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'index.html'

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
            products = Product.objects.filter(
                Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search))
        else:
            products = Product.objects.all()
        context = self.get_context_data(object_list=products)
        context['products'] = products
        return render(request, self.template_name, context=context)


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


class GetDistricts(View):
    def get(self, request):
        region_name = request.GET.get('region')  # AJAX so‘rovdan viloyat nomini olish
        districts = District.objects.filter(region__name=region_name)  # Viloyatga tegishli tumanlar
        district_list = list(districts.values('id', 'name'))  # JSON uchun list yaratish
        return JsonResponse({'districts': district_list})


class ChangePasswordFormView(FormView):
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


class CartListView(ListView):
    template_name = 'user/cart.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = AboutCart.objects.select_related('product').filter(cart=self.request.user.cart).annotate(
            real_price=F('product__price') - F('thread_discount'))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        subtotal = 0
        for product in self.get_queryset():
            subtotal += product.product.price * product.quantity
        context['subtotal'] = subtotal

        return context


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, slug):
        cart = request.user.cart
        product = Product.objects.get(slug=slug)
        page = request.GET.get('page', '/')
        if AboutCart.objects.filter(cart=cart, product=product, thread_discount=0).exists():
            cart_item = AboutCart.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
            messages.success(self.request, "Added!")
            return redirect(page)
        AboutCart.objects.create(cart=cart, product=product, quantity=1)
        messages.success(self.request, "Added!")
        return redirect(page)

    def post(self, request, slug):
        product = Product.objects.get(slug=slug)
        quantity = request.POST.get('quantity')
        cart = request.user.cart
        page = request.POST.get('page', '/')
        thread_discount = request.POST.get('thread_dis')
        thread_user = request.POST.get('thread_user', None)
        if thread_user:
            aboutcart = AboutCart.objects.get(cart=cart, product=product, thread_discount=thread_discount,
                                              thread_user_id=thread_user)
        else:
            aboutcart = AboutCart.objects.get(cart=cart, product=product, thread_discount=thread_discount)
        if int(quantity) != 0:
            aboutcart.quantity = quantity
            aboutcart.save()
        else:
            aboutcart.delete()
            messages.success(self.request, "Successfully deleted!")
        return redirect(page)


class ProductDeleteView(DeleteView):
    template_name = 'user/cart.html'
    success_url = reverse_lazy('cart')
    slug_url_kwarg = 'slug'
    model = Product

    def get_object(self, queryset=None):
        aboutcart = AboutCart.objects.filter(cart=self.request.user.cart, product__slug=self.kwargs['slug'],
                                             thread_discount=self.request.POST.get('thread_discount'))
        return aboutcart

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Successfully deleted!")
        return super().delete(request, *args, **kwargs)


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'user/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        orders = Order.objects.filter(user=self.request.user).annotate(
            total=Value(0, output_field=IntegerField())).order_by('-created_at')
        return orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        orders = self.get_queryset()
        for order in orders:
            total = 0
            for about in order.about.all():
                total += about.product.price * about.quantity
            order.total += total
            order.save()

        context['cart_items_count'] = cart_items_count
        context['orders'] = orders

        return context


class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request):
        order = Order.objects.create(user=request.user)
        for about in request.user.cart.about.all():
            AboutOrder.objects.create(product=about.product,
                                      quantity=about.quantity,
                                      order=order,
                                      thread_discount=about.thread_discount,
                                      thread_user=about.thread_user,
                                      thread_id=about.thread_id,
                                      thread_status="Waiting")
            about.delete()
        messages.success(self.request, "Ordered!")
        return redirect('orders')


class OrderCancelView(View):
    def get(self, request, pk):
        order = Order.objects.get(id=pk)
        if order.status == "In process":
            order.status = "Canceled"
            order.save()
        messages.warning(self.request, "Canceled! Next time check cart one more time before ordering!!!")
        return redirect('orders')

    def post(self, request, pk):
        order = Order.objects.get(id=pk)
        if order.status == "In process":
            order.status = "Delivered"
            order.save()
            for about in order.about.all():
                if Thread.objects.filter(id=about.thread_id).exists():
                    thread = Thread.objects.get(id=about.thread_id)
                    thread.sold += about.quantity
                    thread.save()
        messages.success(self.request, "Delivered")
        return redirect('orders')


class KonkursListView(ListView):
    template_name = 'user/konkurs.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        sellers = Seller.objects.annotate(
            sold_products=Sum(
                'products__about_order__quantity',
                filter=Q(products__about_order__order__status='Delivered'),
                default=0
            )
        ).order_by('-sold_products')
        return sellers


class MarketListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'user/market.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        slug = self.kwargs.get('slug')
        products = Product.objects.filter(quantity__gt=0)
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        if slug != 'all':
            products = products.filter(category__slug=slug)
        context['products'] = products
        context['slug'] = slug
        context['cart_items_count'] = cart_items_count
        return context

    def post(self, request, slug):
        search = request.POST.get('search')
        if search:
            products = Product.objects.filter((Q(name__icontains=search) | Q(description__icontains=search) | Q(
                category__name__icontains=search)) & Q(category__slug=slug) & Q(quantity__gt=0))
        else:
            products = Product.objects.filter(quantity__gt=0)
        context = self.get_context_data(object_list=products)
        context['products'] = products
        return render(request, self.template_name, context=context)


class ThreadListView(LoginRequiredMixin, ListView):
    template_name = 'user/threads.html'
    context_object_name = 'threads'

    def get_queryset(self):
        threads = Thread.objects.filter(user=self.request.user).order_by('-created_at')
        return threads

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        context['cart_items_count'] = cart_items_count
        return context


class ThreadCreateView(LoginRequiredMixin, CreateView):
    template_name = 'user/market.html'
    form_class = ThreadModelForm
    model = Thread

    def form_valid(self, form):
        thread = form.save(commit=False)
        thread.user = self.request.user
        thread.save()
        return redirect('threads')

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('market', kwargs={'slug': 'all'})


class ThreadDeleteView(LoginRequiredMixin, DeleteView):
    model = Thread
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        messages.error(self.request, "O'chirildi!")
        return reverse_lazy('threads')


class ThreadDetailView(View):
    def get(self, request, pk):
        thread = Thread.objects.get(id=pk)
        product = Product.objects.filter(id=thread.product_id).annotate(thread_price=F('price') - thread.discount)
        context = {
            'product': product.first(),
            'thread': thread
        }
        return render(request, 'product/thread-detail.html', context)


class ThreadAddToCartView(LoginRequiredMixin, View):
    def get(self, request, slug):
        cart = request.user.cart
        product = Product.objects.get(slug=slug)
        page = request.GET.get('page', '/')
        thread_id = request.GET.get('thread_id')
        thread_discount = request.GET.get('thread_discount')
        thread = Thread.objects.get(id=thread_id)
        if AboutCart.objects.filter(cart=cart, product=product, thread_discount=thread_discount,
                                    thread_user=thread.user).exists():
            cart_item = AboutCart.objects.get(product=product, cart=cart, thread_discount=thread_discount,
                                              thread_user=thread.user)
            cart_item.quantity += 1
            cart_item.save()
            messages.success(self.request, "Added!")
            return redirect(page)
        AboutCart.objects.create(cart=cart, product=product, quantity=1, thread_discount=thread.discount,
                                 thread_user=thread.user, thread_id=thread_id)
        messages.success(self.request, "Added!")
        return redirect(page)

    # def post(self, request, slug):
    #     product = Product.objects.get(slug=slug)
    #     quantity = request.POST.get('quantity')
    #     cart = request.user.cart
    #     page = request.POST.get('page', '/')
    #     aboutcart = get_object_or_404(AboutCart, product=product, cart=cart)
    #     if int(quantity) != 0:
    #         aboutcart.quantity = quantity
    #         aboutcart.save()
    #     else:
    #         aboutcart.delete()
    #         messages.success(self.request, "Successfully deleted!")
    #     return redirect(page)
