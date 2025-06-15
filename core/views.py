# core/views.py
from django.shortcuts import render
from pages.models import Page # ¡Importamos el modelo Page!

def home(request):
    """
    Busca la página marcada como 'página de inicio' en la base de datos
    y la renderiza usando una plantilla genérica de página.
    """
    try:
        # Buscamos la página de inicio publicada más reciente
        homepage = Page.objects.filter(is_homepage=True, status='published').latest('updated_at')
    except Page.DoesNotExist:
        # Si nadie ha marcado una página como inicio, evitamos un error.
        # Podemos renderizar la plantilla estática original o mostrar un mensaje.
        homepage = None

    context = {
        'page': homepage, # La pasamos con el nombre 'page' para reutilizar la plantilla
    }

    # ¡Reutilizamos la plantilla de detalle de página!
    return render(request, 'pages/page_detail.html', context)