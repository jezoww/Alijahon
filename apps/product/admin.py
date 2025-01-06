from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline

from apps.product.models import Product, Category, ProductImage


class ProductImageInline(StackedInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    exclude = ('slug',)
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    exclude = ('slug',)
