import os
import django

# Configura el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tvt.settings')  # Asegúrate de que 'tvt' es el nombre correcto de tu proyecto
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    username='tavata', 
    email='tavata.art@gmail.com', 
    password='@ng3lBTeVeTD', 
    is_staff=True, 
    is_superuser=True
)