import os
import django
from faker import Faker
import random
from django.conf import settings

# Django muhitini sozlash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')  # Loyihangiz nomini kiriting
django.setup()

from apps.product.models import Product, ProductImage  # Product modelini import qiling


def get_random_image():
    # Media papkasidan product papkasining to'liq yo'lini olish
    image_folder = os.path.join(settings.MEDIA_ROOT, 'product')

    # Papka mavjudligini tekshirish
    if not os.path.exists(image_folder):
        raise FileNotFoundError(f"Rasm papkasi topilmadi: {image_folder}")

    # Rasm fayllarini olish
    images = os.listdir(image_folder)
    if not images:
        raise FileNotFoundError("Rasm papkasi bo'sh! Iltimos, rasmlar qo'shing.")

    # Tasodifiy rasmni tanlash
    return os.path.join('product', random.choice(images))  # Fayl yo'lini nisbiy qaytarish


def populate_products(n):
    faker = Faker()
    # for i in range(n):
    #     product = Product(
    #         name=faker.word(),
    #         description=faker.text().capitalize(),
    #         price=round(random.uniform(10000, 1000000), 2),
    #         quantity=random.randint(1, 100),
    #         category_id=random.randint(1, 14)
    #     )
    #     product.save()
    #     ProductImage.objects.create(product=product, image=get_random_image())
    #     print(i)
    # i = 0
    # for product in Product.objects.all():
    #     product.seller_price = product.price * 20 / 100
    #     product.save()
    #     print(i)
    #     i += 1

    print(f"{n} ta mahsulot muvaffaqiyatli qo'shildi!")


if __name__ == '__main__':
    number_of_products = 10000  # Yaratiladigan mahsulotlar soni
    populate_products(number_of_products)
