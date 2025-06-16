from django import template
from django.db.models import Count
from blog.models import Post, PostCategory
from site_settings.models import SiteConfiguration

# This is necessary for Django to discover our custom tags
register = template.Library()


@register.inclusion_tag('blog/partials/_posts_widget.html')
def show_recent_posts():
    """
    Renders a widget with the most recent published posts.
    The number of posts is configured in the SiteConfiguration model.
    """
    try:
        # Get the configuration object from the database
        config = SiteConfiguration.objects.get()
        count = config.recent_posts_widget_count
    except SiteConfiguration.DoesNotExist:
        # If the configuration object hasn't been created yet, use a fallback default
        count = 5 
            
    posts = Post.objects.filter(status='published').order_by('-published_date')[:count]
    
    # We pass a title to the template to make the widget reusable
    return {'posts': posts, 'widget_title': "Recent Posts"}


@register.inclusion_tag('blog/partials/_posts_widget.html')
def show_most_viewed_posts():
    """
    Renders a widget with the most viewed published posts.
    The number of posts is configured in the SiteConfiguration model.
    """
    try:
        config = SiteConfiguration.objects.get()
        count = config.popular_posts_widget_count # Using the new settings field
    except SiteConfiguration.DoesNotExist:
        count = 5 # Fallback

    posts = Post.objects.filter(status='published').order_by('-views_count', '-published_date')[:count]

    # We reuse the same template as the recent posts widget
    return {'posts': posts, 'widget_title': "Most Viewed"}


@register.inclusion_tag('blog/partials/_blog_categories_widget.html')
def show_blog_categories():
    """
    Renders a widget with a list of all blog categories.
    Annotates each category with the count of published posts.
    """
    # Using .annotate() is very efficient. It performs the count in the database.
    categories = PostCategory.objects.annotate(
        num_posts=Count('posts', filter=models.Q(posts__status='published'))
    ).filter(num_posts__gt=0).order_by('-num_posts', 'name') # Only show categories with posts
    
    return {'categories': categories}