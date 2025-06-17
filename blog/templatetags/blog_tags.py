from django import template
from django.db.models import Count, Q
from blog.models import Post, PostCategory
from site_settings.models import SiteConfiguration

register = template.Library()


@register.inclusion_tag('blog/partials/_posts_widget.html')
def show_recent_posts():
    """
    Gets the most recent published posts to be displayed in a widget.
    The number of posts is configured via SiteConfiguration.
    """
    try:
        config = SiteConfiguration.objects.get()
        count = config.recent_posts_widget_count
    except SiteConfiguration.DoesNotExist:
        count = 5  # Fallback value

    posts = Post.objects.filter(status='published').order_by('-published_date')[:count]
    
    # We pass a title key to the template for translation.
    return {'posts': posts, 'widget_title_key': "recent_posts"}


@register.inclusion_tag('blog/partials/_posts_widget.html')
def show_most_viewed_posts():
    """
    Gets the most viewed published posts to be displayed in a widget.
    The number of posts is configured via SiteConfiguration.
    """
    try:
        config = SiteConfiguration.objects.get()
        count = config.popular_posts_widget_count
    except SiteConfiguration.DoesNotExist:
        count = 5  # Fallback value

    posts = Post.objects.filter(status='published').order_by('-views_count', '-published_date')[:count]

    # We reuse the same template but pass a different title key.
    return {'posts': posts, 'widget_title_key': "most_viewed"}


@register.inclusion_tag('blog/partials/_posts_widget.html')
def show_most_commented_posts():
    """
    Gets the most commented published posts to be displayed in a widget.
    The number of posts is configured via SiteConfiguration.
    """
    try:
        config = SiteConfiguration.objects.get()
        count = config.popular_posts_widget_count
    except SiteConfiguration.DoesNotExist:
        count = 5 # Fallback

    most_commented_posts = Post.objects.filter(status='published') \
                                       .annotate(
                                           num_approved_comments=Count(
                                               'comments', 
                                               filter=Q(comments__is_approved=True)
                                           )
                                       ) \
                                       .filter(num_approved_comments__gt=0) \
                                       .order_by('-num_approved_comments', '-published_date')[:count]

    # We reuse the same template one more time with a new title key.
    return {'posts': most_commented_posts, 'widget_title_key': "most_commented"}


@register.inclusion_tag('blog/partials/_blog_categories_widget.html')
def show_blog_categories():
    """
    Gets all blog categories that have at least one published post,
    ordered by the number of posts.
    """
    # Using .annotate() is very efficient. It performs the count in the database.
    categories = PostCategory.objects.annotate(
        num_posts=Count('posts', filter=Q(posts__status='published'))
    ).filter(num_posts__gt=0).order_by('-num_posts', 'name')
    
    return {'categories': categories}