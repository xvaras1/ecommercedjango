# Generated by Django 4.1.5 on 2023-02-12 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_addres_line_2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
