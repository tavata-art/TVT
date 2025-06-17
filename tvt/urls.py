# tvt/urls.py
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    # 1. Definimos nuestra propia URL de logout para que redirija inmediatamente.
    #    La vista LogoutView, si no encuentra una plantilla de confirmación,
    #    redirige al LOGOUT_REDIRECT_URL que definimos en settings.py.
    #    Para forzarlo en algunos casos, se puede especificar next_page.
    #    Pero la clave es NO tener una plantilla logged_out.html.
    # Vamos a probar la forma más limpia.
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # 2. Incluimos el resto de las URLs de auth (login, password_reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    path('summernote/', include('django_summernote.urls')),
]

# URLs que SÍ tendrán el prefijo de idioma (/es/..., /en/...)
urlpatterns += i18n_patterns(
    path('search/', include('search.urls', namespace='search')), # <-- new line with namespace
    path('pages/', include('pages.urls', namespace='pages')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('contact/', include('contact.urls', namespace='contact')),
    path('', include('core.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
