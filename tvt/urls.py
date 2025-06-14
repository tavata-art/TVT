"""
URL configuration for tvt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings          # Importa settings
from django.conf.urls.static import static  # Importa static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('tinymce/', include('tinymce.urls')), 
    # La ruta de 'core' debe ir al final si usa la raíz ''
    path('', include('core.urls')),
]

# ¡AÑADIR ESTO AL FINAL!
# Sirve los archivos media SOLAMENTE si estamos en modo DEBUG (desarrollo).
# En producción, el servidor web (Nginx, Apache) se encargará de esto.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)