# Generated by Django 5.1.4 on 2024-12-19 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0027_order_shipping_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_price',
            field=models.IntegerField(),
        ),
    ]
