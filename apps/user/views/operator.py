from django.contrib import messages
from django.contrib.staticfiles.views import serve
from django.db.models import Value, Q
from django.db.models.fields import IntegerField
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from apps.user.models import Order, Withdraw, Region


class OperatorPageListView(ListView):
    template_name = 'operator/operator_panel.html'
    context_object_name = 'orders'

    def get_queryset(self):
        order_status = self.request.GET.get('order_status', 'all')
        if order_status == 'all':
            orders = Order.objects.all().annotate(
                total=Value(0, output_field=IntegerField())).order_by('-created_at')
        else:
            orders = Order.objects.filter(status=order_status).annotate(
                total=Value(0, output_field=IntegerField())).order_by('-created_at')

        search = self.request.GET.get('search')
        if search:
            orders = orders.filter(Q(id=search) | Q(user__phone=search))

        for order in orders:
            total = 0
            for about in order.about.all():
                total += (about.product.price - about.thread_discount) * about.quantity
            order.total += total
            order.total += order.shipping_price
            order.save()

        return orders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        order_status = self.request.GET.get('order_status')
        context['order_status'] = order_status
        context['regions'] = Region.objects.all()
        return context


class ChangeStatusOrderView(View):
    def post(self, request, pk):
        order = Order.objects.get(id=pk)
        status = request.POST.get('status')
        order_status = request.GET.get('order_status')
        if status:
            order.status = status
            order.save()
            messages.success(request, "Saqlandi!")

        base_url = reverse('operator')
        query_string = f"?order_status={order_status}"
        full_url = f"{base_url}{query_string}"
        return redirect(full_url)


class ChangeLocationOrderView(View):
    def post(self, request, pk):
        order = Order.objects.get(id=pk)
        location = request.POST.get('location')
        order_status = request.GET.get('order_status')
        if location:
            order.location = location
            order.save()
            messages.success(request, "Saqlandi!")

        base_url = reverse('operator')
        query_string = f"?order_status={order_status}"
        full_url = f"{base_url}{query_string}"
        return redirect(full_url)


class AdminWithdrawListView(ListView):
    template_name = 'operator/admin-withdraws.html'
    context_object_name = 'withdraws'

    def get_queryset(self):
        query = Withdraw.objects.filter(status='waiting')
        return query


class CheckWithdrawView(View):
    def post(self, request, pk):
        withdraw = Withdraw.objects.get(id=pk)
        image = request.FILES.get('image')
        description = request.POST.get('description')
        status = request.POST.get('status')
        user = withdraw.user
        if not status:
            messages.error(request, "Something went wrong!")
        if image and status == "paid":
            withdraw.image = image
            user.money -= withdraw.amount
            user.save()
        elif description and status == "canceled":
            user.money += withdraw.amount
            user.save()
            withdraw.description = description
        else:
            messages.error(request, "Rasm yoki description unutib qoldirildi")
            return redirect('admin-withdraw')
        withdraw.status = status
        withdraw.save()
        messages.success(request, "Done!")
        return redirect('admin-withdraw')
