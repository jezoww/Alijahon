# Generated by Django 5.1.4 on 2024-12-20 18:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0028_alter_order_shipping_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=20)),
                ('owner_of_card', models.CharField(max_length=255)),
                ('amount', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('Paid', 'Paid'), ('canceled', 'Canceled')], max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='check/')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='withdraw_histories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
