# Generated by Django 5.0.6 on 2024-06-05 07:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0020_alter_billofmaterials_options_alter_items_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50, unique=True)),
                ('customer_name', models.CharField(max_length=100)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('packaging_types', models.ManyToManyField(blank=True, to='inventory.packagingtypes')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('contact_info', models.TextField()),
                ('packaging_materials', models.ManyToManyField(blank=True, related_name='suppliers', to='inventory.packagingmaterials')),
            ],
        ),
    ]
