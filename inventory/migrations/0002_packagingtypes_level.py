# Generated by Django 5.0.6 on 2024-05-28 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='packagingtypes',
            name='level',
            field=models.CharField(choices=[('Primary', 'Primary'), ('Secondary', 'Secondary'), ('Tertiary', 'Tertiary')], default='Primary', max_length=10),
        ),
    ]
