# Generated by Django 5.1.4 on 2024-12-18 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_aboutorder_thread_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='money',
            field=models.BigIntegerField(default=0),
        ),
    ]
