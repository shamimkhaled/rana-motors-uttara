# Generated by Django 4.0.3 on 2024-05-06 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0143_alter_customer_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyreport',
            name='datetime',
            field=models.DateTimeField(null=True),
        ),
    ]