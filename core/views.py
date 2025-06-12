from django.shortcuts import render

# Create your views here.
def home(request):
    """
    Renderiza la página de inicio del sitio.
    """
    return render(request, 'core/home.html')