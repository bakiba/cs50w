# Generated by Django 3.1.6 on 2021-03-10 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20210228_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='duration',
            field=models.IntegerField(choices=[(3, '3'), (5, '5'), (7, '7'), (10, '10'), (30, '30')], default=30),
        ),
    ]