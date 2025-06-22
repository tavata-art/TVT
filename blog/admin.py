# File: blog/admin.py
import logging
from django.contrib import admin
from django.db.models import Count # Required for Count() in CommentAdmin's save_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings # Required for dynamically generating search fields

# Third-party imports (ensure these are installed and in INSTALLED_APPS)
from django_summernote.admin import SummernoteModelAdmin # For WYSIWYG editor on Post
from modeltranslation.admin import TabbedTranslationAdmin # For multilingual admin
from mptt.admin import MPTTModelAdmin # For tree display on Comment
from modeltranslation.translator import translator, NotRegistered # For dynamic admin fields

# Local application imports (ensure these models exist)
from .models import Post, Comment # PostCategory is no longer in blog.models
from categories.models import Category # Universal Category model
from site_settings.models import SiteConfiguration # For configurable settings

# Import the Tag model, needed for custom TagAdmin setup
from taggit.models import Tag


logger = logging.getLogger(__name__)

# --- Helper functions for dynamic admin fields ---
# These functions are defined here to be self-contained within blog/admin.py.
# If they are used across many admin files, it's better to move them to a shared utility file (e.g., core/admin_helpers.py)
# and import them from there.

def get_language_aware_prepopulated_fields(model_kls):
    """
    Dynamically generates the prepopulated_fields dictionary for a ModelAdmin,
    considering translatable slug and title/name fields for all configured languages.
    """
    prepopulated_fields_dict = {}
    
    # Get translation options for the given model
    trans_opts = None
    try:
        trans_opts = translator.get_options_for_model(model_kls)
    except NotRegistered:
        logger.warning(f"Model {model_kls.__name__} not registered for translation. "
                       f"Dynamic prepopulated_fields might be incomplete.")
        return prepopulated_fields_dict # Return empty dict if not translatable

    # Check if the model has a 'slug' field and a 'title' or 'name' field that is translatable
    has_slug = hasattr(model_kls, 'slug')
    has_translatable_title = 'title' in trans_opts.fields if trans_opts else False
    has_translatable_name = 'name' in trans_opts.fields if trans_opts else False

    if has_slug and (has_translatable_title or has_translatable_name):
        source_field_name = 'title' if has_translatable_title else 'name'
        for lang_code, _ in settings.LANGUAGES:
            # For each language, link the slug field (e.g., 'slug_en')
            # to the corresponding title/name field (e.g., 'title_en' or 'name_en').
            prepopulated_fields_dict[f'slug_{lang_code}'] = (f'{source_field_name}_{lang_code}',)
    
    # Special handling for `Menu` model where slug is not translatable but derived from a translatable title
    # This block is specific to the `Menu` model ONLY if it is included in this admin.
    # It would typically be in `menus/admin.py`, but leaving it here for completeness if needed elsewhere.
    if model_kls.__name__ == 'Menu' and has_slug and has_translatable_title:
        # Assuming 'Menu' model's slug is not translatable, but its 'title' is.
        # This will prepopulate the single 'slug' field from the title of the default language.
        prepopulated_fields_dict['slug'] = (f'title_{settings.LANGUAGE_CODE}',)

    return prepopulated_fields_dict


def get_language_aware_search_fields(model_kls, fields_to_include=None):
    """
    Dynamically generates a tuple of search fields for a model in all configured languages.
    Assumes common translatable text fields ('title', 'name', 'content', 'description').
    """
    search_fields_list = []
    trans_opts = None
    try:
        trans_opts = translator.get_options_for_model(model_kls)
    except NotRegistered:
        # If the model is not registered for translation, return only basic non-translated fields if specified.
        # Or an empty tuple if no specific fields are requested.
        return (fields_to_include,) if fields_to_include else tuple()

    # Determine which translatable fields to use for search
    actual_fields_to_search = fields_to_include if fields_to_include else trans_opts.fields

    for lang_code, _ in settings.LANGUAGES:
        for field_name in actual_fields_to_search:
            if field_name in trans_opts.fields: # Ensure the field is actually translatable
                search_fields_list.append(f'{field_name}_{lang_code}')
            # If default non-translatable fields should also be included in search, add them here
            # For example: if 'id' or other non-translatable fields are in fields_to_include, add them directly.

    return tuple(search_fields_list)

class TagAdmin(TabbedTranslationAdmin): # <-- THIS IS KEY! Must inherit from TabbedTranslationAdmin
    """
    Custom Admin for Taggit's Tag model.
    It integrates modeltranslation to allow translation of tag names directly in the admin.
    """
    list_display = ('name',) # Display the 'name' field, which TabbedTranslationAdmin will handle
    list_display_links = ('name',) # Clickable by name
    ordering = ('name',) # Order by the currently active language's name

    # Search fields must target translated fields
    search_fields = get_language_aware_search_fields(Tag, fields_to_include=['name']) # Uses name_en, name_es, etc.
    
    # prepopulated_fields will use translated name fields for slug
    # Tag.slug is generally not translated, but derived from the name of the default language
    prepopulated_fields = {'slug': (f'name_{settings.LANGUAGE_CODE}',)}

    # Ensure 'name' and 'slug' fields appear in the form.
    # TabbedTranslationAdmin patches 'name' to show tabs automatically.
    fields = ('name', 'slug') # Only list 'name' and 'slug' here.


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
    
    # Dynamically generate search_fields using the helper function for 'title' and 'content'
    search_fields = get_language_aware_search_fields(Post, fields_to_include=['title', 'content'])

    # Dynamically generate prepopulated_fields for slugs in all languages.
    # Assumes 'Post.slug' is translatable AND 'Post.title' is translatable.
    prepopulated_fields = get_language_aware_prepopulated_fields(Post)

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
    search_fields = ('content', 'author_name', 'author_email') # These are typically not translatable
    readonly_fields = ('post', 'parent', 'user', 'author_name', 'author_email', 'content', 'created_at')
    
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