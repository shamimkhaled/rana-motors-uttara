# Generated by Django 4.0.3 on 2024-06-02 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0146_alter_dailyreport_options_corportepay_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyreport',
            name='reporttype',
            field=models.CharField(blank=True, choices=[('COMMISION', 'COMMISION'), ('DISCOUNT', 'DISCOUNT')], max_length=800, null=True),
        ),
    ]