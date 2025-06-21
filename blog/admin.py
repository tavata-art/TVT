# File: blog/admin.py
import logging
from django.contrib import admin
from django.db.models import Count # Required for Count() in CommentAdmin's save_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Required for dynamically generating search fields
from modeltranslation.admin import TabbedTranslationAdmin # Required for multilingual admin

# Third-party imports (ensure these are installed and in INSTALLED_APPS)
from django_summernote.admin import SummernoteModelAdmin # For WYSIWYG editor on Post
from mptt.admin import MPTTModelAdmin # For tree display on Comment
from modeltranslation.translator import translator # Will be used for dynamic prepopulated_fields

# Local application imports (ensure these models exist in blog.models, categories.models, site_settings.models)
from .models import Post, Comment # PostCategory is no longer in blog.models
from categories.models import Category # Universal Category model
from site_settings.models import SiteConfiguration # For configurable settings

logger = logging.getLogger(__name__)

# --- Generic helper for dynamically generating search_fields and prepopulated_fields ---
# This function helps to avoid code duplication in each Admin class.
def get_language_aware_admin_fields(model_kls):
    search_fields_list = []
    prepopulated_fields_dict = {}
    
    # Get translatable fields from modeltranslation's registry for the given model
    trans_opts = None
    try:
        trans_opts = translator.get_options_for_model(model_kls)
    except translator.NotRegistered:
        pass # Model is not registered for translation, so no language-specific fields will be added

    for lang_code, _ in settings.LANGUAGES:
        # Add basic translatable text fields to search_fields
        if trans_opts:
            for field_name in trans_opts.fields:
                # Assuming simple CharField or TextField equivalents
                search_fields_list.append(f'{field_name}_{lang_code}')
        
        # Specific for models that have a slug linked to a title
        if hasattr(model_kls, 'slug') and hasattr(model_kls, 'title_en'): # Checking if model has a slug and translated titles
            prepopulated_fields_dict[f'slug_{lang_code}'] = (f'title_{lang_code}',)
            
    return tuple(search_fields_list), prepopulated_fields_dict


# --- ADMIN FOR POST CATEGORIES (if Category model were still here, but it's not) ---
# PostCategoryAdmin is removed as Category is now in categories.models

# --- ADMIN FOR BLOG POSTS ---
@admin.register(Post)
class PostAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    """
    Admin options for the Post model, integrating Summernote for content,
    ModelTranslation for multilingual fields, and managing categories via ManyToMany.
    """
    list_display = ('title', 'author', 'status', 'published_date', 'views_count', 'editor_rating', 'display_categories_list')
    list_filter = ('status', 'published_date', 'author')
    date_hierarchy = 'published_date'
    ordering = ('status', '-published_date')
    list_editable = ('status', 'editor_rating')
    
    # Generate search_fields and prepopulated_fields dynamically
    _search_fields, _prepopulated_fields = get_language_aware_admin_fields(Post)
    search_fields = _search_fields
    prepopulated_fields = _prepopulated_fields

    # Summernote fields must be specified for each language (e.g., 'content_en')
    summernote_fields = tuple([f'content_{lang_code}' for lang_code, _ in settings.LANGUAGES])
    
    # ManyToManyField for categories, uses a nice multi-selector interface
    filter_horizontal = ('categories',) 

    # Custom method to display categories in the list view
    @admin.display(description=_("Categories"))
    def display_categories_list(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])


# --- ADMIN FOR COMMENTS ---
@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    """
    Admin options for the Comment model.
    Uses MPTTModelAdmin for tree display and includes logic for user promotion.
    """
    list_display = ('__str__', 'post', 'author_name', 'created_at', 'is_approved')
    list_display_links = ('__str__',)
    list_filter = ('is_approved', 'created_at', 'post')
    list_editable = ('is_approved',)
    search_fields = ('content', 'author_name', 'author_email') # Assuming these fields are not translatable directly on Comment
    readonly_fields = ('post', 'parent', 'user', 'author_name', 'author_email', 'content', 'created_at')

    # Assigns a dynamic property to mptt_level_indent for tree view indentation
    @property
    def mptt_level_indent(self):
        try:
            return SiteConfiguration.objects.get().comment_indentation_pixels
        except SiteConfiguration.DoesNotExist:
            logger.warning("SiteConfiguration not found. Using default mptt_level_indent of 20.")
            return 20

    def save_model(self, request, obj, form, change):
        """
        Custom save logic to auto-promote users to 'Trusted Commenter' status
        when their comments are approved.
        """
        super().save_model(request, obj, form, change)
        
        # User promotion logic (remains the same)
        if 'is_approved' in form.changed_data and obj.is_approved and obj.user:
            try:
                user_profile = obj.user.profile
                if not user_profile.is_trusted_commenter:
                    try:
                        config = SiteConfiguration.objects.get()
                        approval_threshold = config.trusted_commenter_threshold
                    except SiteConfiguration.DoesNotExist:
                        approval_threshold = 10 
                        logger.warning("SiteConfiguration not found. Using default commenter threshold of 10.")
                    
                    approved_comment_count = Comment.objects.filter(user=obj.user, is_approved=True).count()
                    
                    if approved_comment_count >= approval_threshold:
                        user_profile.is_trusted_commenter = True
                        user_profile.save(update_fields=['is_trusted_commenter'])
                        logger.info(f"User '{obj.user.username}' auto-promoted to Trusted Commenter.")
            except Exception as e:
                logger.error(f"Error during user promotion logic for user '{obj.user.username}': {e}", exc_info=True)
