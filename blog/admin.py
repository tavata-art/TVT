# File: blog/admin.py
import logging
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

# Third-party imports
from django_summernote.admin import SummernoteModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from mptt.admin import MPTTModelAdmin

# Local application imports
from .models import Post, Comment
from categories.models import Category  # Import the universal Category model
from site_settings.models import SiteConfiguration

# Get a logger instance for this module
logger = logging.getLogger(__name__)


# This inline allows managing categories directly from the Post/Page change pages
class CategoryInline(GenericTabularInline):
    model = Category
    extra = 1
    fields = ('name', 'slug', 'parent') 
    prepopulated_fields = {'slug': ('name',)}
    verbose_name = _("Category")
    verbose_name_plural = _("Categories")


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    """ Admin options for the Post model. """
    list_display = ('title', 'author', 'status', 'published_date', 'views_count', 'editor_rating')
    list_filter = ('status', 'published_date', 'author')
    search_fields = ('title_en', 'content_en', 'title_es', 'content_es', 'title_ca', 'content_ca')
    date_hierarchy = 'published_date'
    ordering = ('status', '-published_date')
    list_editable = ('status', 'editor_rating')
    prepopulated_fields = {'slug_en': ('title_en',), 'slug_es': ('title_es',), 'slug_ca': ('title_ca',)}
    summernote_fields = ('content_en', 'content_es', 'content_ca')
    filter_horizontal = ('categories',)


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    """ 
    Admin options for the Comment model, using MPTT for tree display
    and including logic for auto-promoting trusted users.
    """
    list_display = ('__str__', 'post', 'author_name', 'created_at', 'is_approved')
    list_display_links = ('__str__',)
    list_filter = ('is_approved', 'created_at', 'post')
    list_editable = ('is_approved',)
    search_fields = ('content', 'author_name', 'author_email')
    readonly_fields = ('post', 'parent', 'user', 'author_name', 'author_email', 'content', 'created_at')

    def get_mptt_level_indent(self, obj=None):
        """ Gets the indentation value from the site configuration for the tree view. """
        try:
            return SiteConfiguration.objects.get().comment_indentation_pixels
        except SiteConfiguration.DoesNotExist:
            logger.warning("SiteConfiguration not found. Using default mptt_level_indent of 20.")
            return 20
    
    # This assigns our dynamic method to the class attribute that mptt-admin expects.
    mptt_level_indent = property(get_mptt_level_indent)

    def save_model(self, request, obj, form, change):
        """
        Custom save logic to auto-promote users to 'Trusted Commenter' status
        when their comments are approved.
        """
        super().save_model(request, obj, form, change)
        
        if 'is_approved' in form.changed_data and obj.is_approved and obj.user:
            try:
                user_profile = obj.user.profile
                if not user_profile.is_trusted_commenter:
                    try:
                        config = SiteConfiguration.objects.get()
                        approval_threshold = config.trusted_commenter_threshold
                    except SiteConfiguration.DoesNotExist:
                        approval_threshold = 10
                        logger.warning("SiteConfiguration not found. Using default commenter threshold.")
                    
                    approved_comment_count = Comment.objects.filter(user=obj.user, is_approved=True).count()
                    
                    if approved_comment_count >= approval_threshold:
                        user_profile.is_trusted_commenter = True
                        user_profile.save(update_fields=['is_trusted_commenter'])
                        logger.info(f"User '{obj.user.username}' auto-promoted to Trusted Commenter.")
            except Exception as e:
                logger.error(f"Error during user promotion logic for user '{obj.user.username}': {e}", exc_info=True)