from django.urls import path

from apps.user.views import OrderListView, CreateOrderView, OrderCancelView, OrderDetail

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders'),
    path('order/', CreateOrderView.as_view(), name='order'),
    path('cancel-order/<int:pk>', OrderCancelView.as_view(), name='cancel-order'),
    path('get-order-details/<int:pk>', OrderDetail.as_view(), name='get_order_details')
]
