from unicodedata import category

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F, Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DeleteView

from apps.product.models import Product, Category
from apps.user.forms import ThreadModelForm
from apps.user.models import AboutCart, Thread, \
    VisitedIpAddresses


class MarketListView(ListView):
    context_object_name = 'products'
    template_name = 'user/market.html'
    paginate_by = 15

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        if slug != 'all':
            products = Product.objects.prefetch_related('images').select_related('category').filter(category__slug=slug,
                                                                                                    quantity__gt=0)
        else:
            products = Product.objects.prefetch_related('images').select_related('category').filter(quantity__gt=0)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        categories = Category.objects.all()
        if self.request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        else:
            cart_items_count = 0

        slug = self.kwargs.get('slug')
        context['slug'] = slug
        context['categories'] = categories
        context['cart_items_count'] = cart_items_count
        return context

    def post(self, request, slug):
        search = request.POST.get('search')
        categories = Category.objects.all()
        products = self.get_queryset()
        if search:
            products = products.filter(
                (Q(name__icontains=search) | Q(description__icontains=search) | Q(
                    category__name__icontains=search)) & Q(category__slug=slug) & Q(quantity__gt=0))
        context = self.get_context_data(object_list=products)
        context['products'] = products
        context['categories'] = categories
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
        ip = request.META.get('REMOTE_ADDR')
        if not VisitedIpAddresses.objects.filter(thread=thread, ip=ip):
            VisitedIpAddresses.objects.create(thread=thread, ip=ip)
        if request.user.is_authenticated:
            cart_items_count = AboutCart.objects.filter(cart=request.user.cart).count()
        else:
            cart_items_count = 0
        context = {
            'product': product.first(),
            'thread': thread,
            'cart_items_count': cart_items_count,
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


class StatisticsListView(LoginRequiredMixin, ListView):
    template_name = 'user/statistics.html'
    context_object_name = 'threads'

    def get_queryset(self):
        query = Thread.objects.filter(user=self.request.user).prefetch_related('IPs').annotate(visited=Count('IPs'))
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items_count = AboutCart.objects.filter(cart=self.request.user.cart).count()
        total_visited = 0
        total_delivering = 0
        total_delivered = 0
        total_canceled = 0
        for thread in self.get_queryset():
            total_visited += thread.visited
            total_delivering += thread.delivering
            total_delivered += thread.sold
            total_canceled += thread.canceled

        context['total_visited'] = total_visited
        context['total_delivering'] = total_delivering
        context['total_delivered'] = total_delivered
        context['total_canceled'] = total_canceled
        context['cart_items_count'] = cart_items_count

        return context
