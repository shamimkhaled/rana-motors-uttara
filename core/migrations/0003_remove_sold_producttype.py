# Generated by Django 4.0.3 on 2024-08-16 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_sold_soldproducttype_alter_sold_producttype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sold',
            name='producttype',
        ),
    ]
