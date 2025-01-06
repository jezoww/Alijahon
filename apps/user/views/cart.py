from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView

from apps.product.models import Product
from apps.user.models import AboutCart, DeliveryPrice


class CartListView(LoginRequiredMixin, ListView):
    template_name = 'user/cart.html'
    context_object_name = 'products'

    def get_queryset(self):
        AboutCart.objects.filter(product__quantity=0).delete()
        queryset = AboutCart.objects.select_related('product').filter(cart=self.request.user.cart).annotate(
            real_price=F('product__price') - F('thread_discount'))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        subtotal = 0
        if self.request.user.profile.district and self.request.user.cart.about.all():
            delivery_price = DeliveryPrice.objects.get(region=self.request.user.profile.district.region).price
        else:
            delivery_price = 0
        for product in self.get_queryset():
            subtotal += product.product.price * product.quantity
        context['delivery_price'] = delivery_price
        context['subtotal'] = subtotal
        return context


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, slug):
        cart = request.user.cart
        product = Product.objects.get(slug=slug)
        page = request.GET.get('page', '/')
        if product.quantity == 0:
            messages.error(request, "Something went wrong! Do not try to hack! Please!!!")
            return redirect(page)
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
        if product.quantity < int(quantity):
            messages.error(request,
                           f"{quantity} ta ''{product.name}'' qolmagan. Faqatgina {product.quantity} ta qolgan.")
            return redirect('cart')
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
