# Generated by Django 4.0.3 on 2024-08-13 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_customer_phone2_remove_supplier_phone2'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='Phone2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='Phone2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
