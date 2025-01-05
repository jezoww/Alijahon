from django.urls import path

from apps.user.views import CartListView, AddToCartView, ProductDeleteView

urlpatterns = [
    path('cart/', CartListView.as_view(), name='cart'),
    path('add-to-cart/<str:slug>', AddToCartView.as_view(), name='add-to-cart'),
    path('delete-product/<str:slug>', ProductDeleteView.as_view(), name='delete-product'),
]
