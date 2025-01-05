from django.db.models import *
from django.utils.text import slugify


class BaseSlug(Model):
    class Meta:
        abstract = True

    name = CharField(max_length=255)
    slug = SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = self.slug + "1"
        return super().save(*args, **kwargs)


class Category(BaseSlug):
    image = ImageField(upload_to='category/')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(BaseSlug):
    description = CharField(max_length=512)
    price = PositiveIntegerField()
    category = ForeignKey(Category, on_delete=CASCADE, related_name='products')
    seller_price = IntegerField(default=0)
    quantity = PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class ProductImage(Model):
    image = ImageField(upload_to='product/')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='images')
