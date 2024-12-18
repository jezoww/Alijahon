from django.urls import path

from apps.product.views import ProductDetailView, ProductsByCategoryView, ProductListView, LikedProductsListView

urlpatterns = [
    path('product/<str:slug>', ProductDetailView.as_view(), name='product-detail'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<str:slug>', ProductsByCategoryView.as_view(), name='products-by-category'),
    path('liked-products/', LikedProductsListView.as_view(), name='liked-products'),
]
