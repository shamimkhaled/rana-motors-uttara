# Generated by Django 4.0.3 on 2024-08-16 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_sold_productype_sold_soldproductype1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sold',
            old_name='soldproductype1',
            new_name='posproductype',
        ),
    ]