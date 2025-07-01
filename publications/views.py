# File: publications/views.py
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language
from .models import Publication

def publication_detail_view(request, slug):
    """
    📘 Shows the detail of a single scientific publication.
    """
    language = get_language()
    publication = get_object_or_404(Publication, translations__slug=slug, is_published=True)

    context = {
        "publication": publication,
        "title": publication.safe_translation_getter("title", any_language=True),
        "meta_title": publication.safe_translation_getter("meta_title", any_language=True),
        "meta_description": publication.safe_translation_getter("meta_description", any_language=True),
    }
    return render(request, "publications/publication_detail.html", context)

