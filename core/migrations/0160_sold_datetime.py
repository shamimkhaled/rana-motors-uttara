# Generated by Django 4.0.3 on 2024-06-09 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0159_rename_price_plreport_costprice_plreport_price1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sold',
            name='datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]