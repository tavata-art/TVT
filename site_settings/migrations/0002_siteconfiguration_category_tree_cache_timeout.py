# Generated by Django 5.2.3 on 2025-06-19 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='category_tree_cache_timeout',
            field=models.PositiveIntegerField(default=43200, help_text='How long the full category tree should be stored in cache. High values are recommended.', verbose_name='Category Tree Cache Timeout (in seconds)'),
        ),
    ]
