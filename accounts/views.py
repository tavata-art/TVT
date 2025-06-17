# accounts/views.py
from django.contrib.auth import views as auth_views

class CustomLogoutView(auth_views.LogoutView):
    # La única personalización que necesitamos es decirle
    # a dónde ir después del logout.
    # Esto sobreescribe el LOGOUT_REDIRECT_URL de settings.py
    # y elimina la necesidad de la página de confirmación.
    next_page = '/' 
