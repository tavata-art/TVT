import os
import sys

# Asegura que el directorio del proyecto esté en el PATH
project_home = '/home/sextavac/tvt'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configura la variable DJANGO_SETTINGS_MODULE a tu settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'tvt.settings'

# Obtén la aplicación WSGI de Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()