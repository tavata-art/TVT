# File: blog/admin.py
import logging
from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

# Third-party imports
from django_summernote.admin import SummernoteModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from mptt.admin import MPTTModelAdmin

# Local application imports
from .models import Post, PostCategory, Comment
from site_settings.models import SiteConfiguration

# Get a logger instance for this module
logger = logging.getLogger(__name__)


@admin.register(PostCategory)
class PostCategoryAdmin(TabbedTranslationAdmin):
    """ Admin options for the PostCategory model. """
    list_display = ('name', 'slug') # modeltranslation will show the current language
    search_fields = ('name_en', 'name_es', 'name_ca')
    prepopulated_fields = {'slug_en': ('name_en',), 'slug_es': ('name_es',), 'slug_ca': ('name_ca',)}


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    """ Admin options for the Post model, integrating Summernote and ModelTranslation. """
    list_display = ('title', 'author', 'status', 'published_date', 'views_count', 'editor_rating')
    list_filter = ('status', 'published_date', 'author', 'categories')
    search_fields = ('title_en', 'content_en', 'title_es', 'content_es', 'title_ca', 'content_ca')
    date_hierarchy = 'published_date'
    ordering = ('status', '-published_date')
    list_editable = ('status', 'editor_rating')
    prepopulated_fields = {'slug_en': ('title_en',), 'slug_es': ('title_es',), 'slug_ca': ('title_ca',)}
    filter_horizontal = ('categories',)
    summernote_fields = ('content_en', 'content_es', 'content_ca')


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
    
    # We make these fields read-only to prevent admins from editing user-submitted content.
    # The 'parent' field should be managed via the tree interface.
    readonly_fields = ('post', 'parent', 'user', 'author_name', 'author_email', 'content', 'created_at')
    
    def get_mptt_level_indent(self, obj=None):
        """ Gets the indentation value from the site configuration for the tree view. """
        try:
            return SiteConfiguration.objects.get().comment_indentation_pixels
        except SiteConfiguration.DoesNotExist:
            logger.warning("SiteConfiguration not found. Using default mptt_level_indent.")
            return 20
    
    mptt_level_indent = property(get_mptt_level_indent)

    def save_model(self, request, obj, form, change):
        """
        Custom save logic to auto-promote users to 'Trusted Commenter' status
        when their comments are approved.
        """
        # Save the comment object first to ensure its state is updated in the DB
        super().save_model(request, obj, form, change)
        
        # --- USER PROMOTION LOGIC ---
        # We only check for promotion if the 'is_approved' field changed to True
        # and the comment was made by a registered user.
        if 'is_approved' in form.changed_data and obj.is_approved and obj.user:
            try:
                user_profile = obj.user.profile
                
                # If the user is not already trusted, we perform the check.
                if not user_profile.is_trusted_commenter:
                    try:
                        config = SiteConfiguration.objects.get()
                        approval_threshold = config.trusted_commenter_threshold
                    except SiteConfiguration.DoesNotExist:
                        approval_threshold = 10 # Fallback
                        logger.warning("SiteConfiguration not found. Using default commenter threshold of 10.")
                    
                    approved_comment_count = Comment.objects.filter(user=obj.user, is_approved=True).count()
                    
                    if approved_comment_count >= approval_threshold:
                        user_profile.is_trusted_commenter = True
                        user_profile.save(update_fields=['is_trusted_commenter'])
                        logger.info(f"User '{obj.user.username}' has been auto-promoted to a Trusted Commenter (threshold: {approval_threshold}).")
            
            except User.profile.RelatedObjectDoesNotExist:
                 logger.warning(f"Attempted to promote user '{obj.user.username}' but they have no profile.")
            except Exception as e:
                logger.error(f"Error during user promotion logic for user '{obj.user.username}': {e}", exc_info=True)
