from itertools import product

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, CharField, PasswordInput
from phonenumber_field.formfields import PhoneNumberField

from apps.product.models import Product
from apps.user.models import User, Region, District, Profile, Thread


class RegisterModelForm(ModelForm):
    class Meta:
        model = User
        fields = 'phone', 'password'

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.country_code == 998:
            raise ValidationError('Please enter Uzbekistan phone number')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Phone number already registered!")
        return phone

    def clean_password(self):
        password = self.cleaned_data['password']
        return make_password(password)


class LoginForm(Form):
    phone = PhoneNumberField(region='UZ')
    password = CharField(widget=PasswordInput())

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not User.objects.filter(phone=phone).exists():
            raise ValidationError("Phone number not found!")
        return phone


class ProfileModelForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'district', 'additional_info_location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean_district(self):
        district = self.data.get('district')
        if district:
            if not District.objects.filter(id=int(district)).exists():
                raise ValidationError('Something went wrong!')
        return district


class ChangePasswordForm(Form):
    password = CharField(max_length=555)
    new_password = CharField(max_length=555)
    confirm_new_password = CharField(max_length=555)

    def clean_new_password(self):
        new_password = self.data.get('new_password')
        confirm_new_password = self.data.get('confirm_new_password')
        if new_password != confirm_new_password:
            raise ValidationError('Passwords must match! PLease enter the same passwords!')
        return new_password


class ThreadModelForm(ModelForm):
    class Meta:
        model = Thread
        exclude = 'created_at', 'user', 'sold'

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        product_id = self.data.get('product')
        product = Product.objects.get(id=product_id)
        if int(product.seller_price) < discount:
            raise ValidationError("Please enter less discount than the limit of product!")
        return discount

