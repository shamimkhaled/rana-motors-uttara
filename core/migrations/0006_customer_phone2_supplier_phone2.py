# Generated by Django 4.0.3 on 2024-08-13 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_customer_balance2'),
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