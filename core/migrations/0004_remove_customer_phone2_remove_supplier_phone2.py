# Generated by Django 4.0.3 on 2024-08-13 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_customer_phone2_supplier_phone2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='Phone2',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='Phone2',
        ),
    ]
