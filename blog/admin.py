from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Post, PostCategory, Comment
from django_summernote.admin import SummernoteModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from mptt.admin import MPTTModelAdmin
from site_settings.models import SiteConfiguration

@admin.register(PostCategory)
class PostCategoryAdmin(TabbedTranslationAdmin):
    """ Admin options for the PostCategory model. """
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin, TabbedTranslationAdmin):
    """ Admin options for the Post model, integrating Summernote and ModelTranslation. """
    
    list_display = ('title', 'author', 'status', 'published_date')
    list_filter = ('status', 'published_date', 'author', 'categories')
    search_fields = ('title', 'content')
    date_hierarchy = 'published_date'
    ordering = ('status', '-published_date')
    
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories',)
    summernote_fields = ('content',)

# --- NEW ADMIN CLASS FOR COMMENTS ---
@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ('__str__', 'post', 'author_name', 'created_at', 'is_approved')
    list_display_links = ('__str__',)
    list_filter = ('is_approved', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('content', 'author_name', 'author_email')

    # Definimos el método que MPTT usará para obtener el valor
    def get_mptt_level_indent(self, obj=None):
        try:
            # La consulta a la BD se hace aquí, cuando se renderiza la vista
            return SiteConfiguration.objects.get().comment_indentation_pixels
        except SiteConfiguration.DoesNotExist:
            # Fallback si la configuración no existe
            return 20

    mptt_level_indent = property(get_mptt_level_indent)