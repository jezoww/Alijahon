from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import *
from phonenumber_field.modelfields import PhoneNumberField

from apps.product.models import Product


class CustomUserManager(UserManager):
    def _create_user(self, phone, email, password, **extra_fields):
        if not phone:
            raise ValueError("The given phone must be set")
        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, email, password, **extra_fields)

    def create_superuser(self, phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, email, password, **extra_fields)


class User(AbstractUser):
    username = None
    phone = PhoneNumberField(region='UZ', unique=True)
    objects = CustomUserManager()
    first_name = None
    last_name = None
    money = BigIntegerField(default=0)

    USERNAME_FIELD = 'phone'
    def __str__(self):
        return str(self.money)


class Profile(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    first_name = CharField(max_length=255, null=True)
    last_name = CharField(max_length=255, null=True)
    district = ForeignKey('District', on_delete=SET_NULL, null=True, related_name='users')
    additional_info_location = CharField(max_length=350)


class Likes(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='likes')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'product')


class Cart(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='cart')


class AboutCart(Model):
    cart = ForeignKey(Cart, on_delete=CASCADE, related_name='about')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='about')
    quantity = PositiveSmallIntegerField()
    thread_discount = IntegerField(default=0)
    thread_user = ForeignKey(User, SET_NULL, null=True)
    thread_id = IntegerField(null=True)


class Order(Model):
    class ORDERSTATUSCHOICE(TextChoices):
        in_process = "In process", "in process"
        canceled = "Canceled", "canceled"
        delivered = "Delivered", "delivered"
        delivering = "Delivering", 'delivering'

    user = ForeignKey(User, on_delete=CASCADE, related_name='orders')
    status = CharField(choices=ORDERSTATUSCHOICE.choices, max_length=100, default="in process")
    created_at = DateTimeField(auto_now_add=True)
    shipping_price = IntegerField()
    location = CharField(max_length=512)

    def save(self, *args, **kwargs):
        if self.status == "Delivered":
            for about in self.about.all():
                if about.thread_status == "Waiting":
                    about.thread_status = "Paid"
                    user = about.thread_user
                    if user:
                        user.money += about.product.seller_price - about.thread_discount
                        user.save()
                    about.save()
        return super().save(*args, **kwargs)


class AboutOrder(Model):
    class THREADSTATUSCHOCICE(TextChoices):
        waiting = "Waiting", "Waiting"
        canceled = "Canceled", "Canceled"
        paid = "Paid", "Paid"

    order = ForeignKey(Order, on_delete=CASCADE, related_name='about')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='about_order')
    quantity = PositiveSmallIntegerField()
    thread_discount = IntegerField(default=0)
    thread_user = ForeignKey(User, SET_NULL, null=True)
    thread_status = CharField(max_length=100, choices=THREADSTATUSCHOCICE.choices, null=True)
    thread_id = IntegerField(null=True)


class Region(Model):
    name = CharField(max_length=255)


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('Region', on_delete=CASCADE, related_name='districts')


class DeliveryPrice(Model):
    region = OneToOneField(Region, on_delete=CASCADE, related_name='price')
    price = DecimalField(max_digits=12, decimal_places=2)


class Thread(Model):
    title = CharField(max_length=155)
    user = ForeignKey(User, on_delete=CASCADE, related_name="threads")
    product = ForeignKey(Product, on_delete=CASCADE, related_name="threads")
    discount = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    sold = IntegerField(default=0)
    delivering = IntegerField(default=0)
    canceled = IntegerField(default=0)


class VisitedIpAddresses(Model):
    thread = ForeignKey(Thread, CASCADE, related_name="IPs")
    ip = CharField(max_length=128)


class BlockedIp(Model):
    ip = CharField(max_length=255)


class Competition(Model):
    image = ImageField(upload_to='konkurs/')
    start_at = DateField()
    end_at = DateField()
    description = TextField()


class Withdraw(Model):
    class STATUSCHOICE(TextChoices):
        waiting = "waiting", "Waiting"
        Paid = "paid", "Paid"
        canceled = "canceled", "Canceled"

    user = ForeignKey(User, SET_NULL, related_name='withdraw_histories', null=True)
    card_number = CharField(max_length=20)
    owner_of_card = CharField(max_length=255)
    amount = IntegerField()
    created_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=50, choices=STATUSCHOICE.choices, default='waiting')
    description = TextField(null=True, blank=True)
    image = ImageField(upload_to='check/', null=True, blank=True)
