# Generated by Django 4.0 on 2022-02-03 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_keyword_book_full_text_category_views_book_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_id',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
