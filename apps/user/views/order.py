from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Value, IntegerField, F
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView

from apps.user.models import AboutCart, Order, AboutOrder, Thread, \
    DeliveryPrice


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
                total += (about.product.price - about.thread_discount) * about.quantity
            order.total += total
            order.total += order.shipping_price
            order.save()

        context['cart_items_count'] = cart_items_count
        context['orders'] = orders

        return context


class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request):
        abouts = request.user.cart.about.all()
        if abouts:
            user = request.user
            if not user.profile.district:
                messages.warning(request, "Before ordering, please add your location.")
                return redirect("cart")
            order = Order.objects.create(user=user, shipping_price=DeliveryPrice.objects.get(
                region=user.profile.district.region).price)
            order.location = f"{user.profile.district.region.name}: {user.profile.district.name}: {user.profile.additional_info_location}"
            order.save()
            for about in abouts:
                product = about.product
                if product.quantity < about.quantity:
                    messages.error(self.request,
                                   f"{product.name} {about.quantity} ta qolmagan. Faqatgina {product.quantity} ta qolgan.")
                    return redirect("cart")
            for about in abouts:
                product = about.product
                AboutOrder.objects.create(product=product,
                                          quantity=about.quantity,
                                          order=order,
                                          thread_discount=about.thread_discount,
                                          thread_user=about.thread_user,
                                          thread_id=about.thread_id,
                                          thread_status="Waiting")
                product.quantity -= about.quantity
                Thread.objects.filter(id=about.thread_id).update(delivering=F('delivering') + about.quantity)
                if product.quantity == 0:
                    AboutCart.objects.filter(product=product).delete()
                product.save()
                about.delete()
            messages.success(self.request, "Ordered!")
            return redirect('orders')
        else:
            messages.warning(request, "You do not have any products.")
            return redirect("cart")


class OrderCancelView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = Order.objects.get(id=pk)
        if order.status == "in process":
            order.status = "canceled"
            order.save()
            for about in order.about.all():
                Thread.objects.filter(id=about.thread_id).update(delivering=F('delivering') - about.quantity,
                                                                 canceled=F('canceled') + about.quantity)
        messages.warning(self.request, "Canceled! Next time check cart one more time before ordering!!!")
        return redirect('orders')

    def post(self, request, pk):
        order = Order.objects.get(id=pk)
        if order.status == "in process":
            order.status = "delivered"
            order.save()
            for about in order.about.all():
                if Thread.objects.filter(id=about.thread_id).exists():
                    Thread.objects.filter(id=about.thread_id).update(sold=F('sold') + about.quantity,
                                                                     delivering=F('delivering') - about.quantity)

        messages.success(self.request, "Delivered")
        return redirect('orders')


class OrderDetail(View):
    def get(self, request, pk):
        order = Order.objects.prefetch_related('about').prefetch_related('about__product').get(id=pk)
        products = []
        for about in order.about.all():
            total = about.product.price * about.quantity
            products.append({"name": about.product.name,
                             "quantity": about.quantity,
                             "price": intcomma(about.product.price),
                             "total": intcomma(total)})
        return JsonResponse({"products": products})
