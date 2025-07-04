# Generated by Django 5.2.3 on 2025-06-28 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widgets', '0003_widget_carousel_interval_ms_alter_widget_widget_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widget',
            name='widget_type',
            field=models.CharField(choices=[('recent_posts', 'Recent Blog Posts'), ('most_viewed_posts', 'Most Viewed Blog Posts'), ('most_commented_posts', 'Most Commented Blog Posts'), ('blog_categories', 'Blog Category List'), ('editor_picks_posts', "Editor's Picks (Blog Posts)"), ('post_grid_recent', 'Post Grid: Recent Posts'), ('post_grid_popular', 'Post Grid: Most Viewed'), ('post_grid_commented', 'Post Grid: Most Commented'), ('post_grid_editor', "Post Grid: Editor's Picks"), ('post_carousel', 'Post Carousel'), ('user_directory', 'User Directory'), ('testimonials', 'Testimonials')], max_length=50, verbose_name='Widget Type'),
        ),
    ]
