# Generated by Django 4.0 on 2022-02-03 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_book_book_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='book_id',
            field=models.CharField(blank=True, default=0, max_length=350),
        ),
    ]
