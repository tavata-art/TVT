from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# ==============================================================================
# URLS THAT SHOULD NOT BE TRANSLATED (e.g., admin, auth process)
# ==============================================================================
urlpatterns = [
    # 1. Django Admin
    path('admin/', admin.site.urls),
    
    # 2. Third-party app URLs (like summernote)
    path('summernote/', include('django_summernote.urls')),
    
    # 3. Custom Authentication URLs
    # This URL for signup comes from our own 'accounts' app.
    # It must come BEFORE the generic include below.
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # This includes all of Django's built-in auth URLs (login, password reset, etc.)
    # Our custom logout is technically handled by django.contrib.auth.urls's default logout,
    # as we now handle the POST request in the template. If we needed a custom
    # next_page, we'd define a specific logout path here BEFORE this include.
    path('accounts/', include('django.contrib.auth.urls')),
]


# ==============================================================================
# URLS THAT WILL BE PREFIXED WITH A LANGUAGE CODE (e.g., /en/blog/, /es/blog/)
# ==============================================================================
urlpatterns += i18n_patterns(
    # Our own apps with content visible to the user
    path('search/', include('search.urls', namespace='search')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('contact/', include('contact.urls', namespace='contact')),

    # Homepage must be the last one in this block
    path('', include('core.urls')),
)


# ==============================================================================
# SERVING MEDIA FILES IN DEVELOPMENT
# ==============================================================================
# This is only for development (DEBUG=True) and should not be used in production.
# The web server (e.g., Nginx) should be configured to serve media files.
if settings.DEBUG:
    # Añadimos las URLs para los archivos MEDIA
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Este es para tus archivos de app (CSS, JS, imágenes por defecto)
    # Es la forma recomendada por Django para desarrollo.
    urlpatterns += staticfiles_urlpatterns()
# ==============================================================================