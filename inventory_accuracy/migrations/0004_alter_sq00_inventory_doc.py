# Generated by Django 4.0.6 on 2022-07-18 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_accuracy', '0003_alter_sq00_inventory_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sq00',
            name='inventory_doc',
            field=models.CharField(max_length=50, null=True),
        ),
    ]