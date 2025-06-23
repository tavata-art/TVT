from django.conf import settings

def languages_context(request):
    return {
        'LANGUAGES': settings.LANGUAGES,
    }