# Generated by Django 4.0.6 on 2022-07-18 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_accuracy', '0002_alter_sq00_tys_alter_sq00_catchment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sq00',
            name='inventory_number',
            field=models.CharField(max_length=50, null=True),
        ),
    ]