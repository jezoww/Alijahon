# Generated by Django 5.1.4 on 2024-12-17 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('In process', 'In process'), ('Canceled', 'Canceled'), ('Delivered', 'Delivered')], default='In process', max_length=100),
        ),
    ]
