# Generated by Django 5.0.6 on 2024-05-30 05:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_packagingtypes_warehouse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='packagingtypes',
            name='warehouse',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='inventory.warehouse'),
        ),
    ]
