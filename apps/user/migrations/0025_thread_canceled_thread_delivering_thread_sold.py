# Generated by Django 5.1.4 on 2024-12-19 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_remove_thread_canceled_remove_thread_delivering_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='canceled',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='thread',
            name='delivering',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='thread',
            name='sold',
            field=models.IntegerField(default=0),
        ),
    ]
