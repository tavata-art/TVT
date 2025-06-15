# tvt/urls.py
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
]

# URLs que SÍ tendrán el prefijo de idioma (/es/..., /en/...)
urlpatterns += i18n_patterns(
    path('pages/', include('pages.urls')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('', include('core.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
