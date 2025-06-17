# core/views.py
import logging
from django.shortcuts import render
from pages.models import Page

# Get a logger instance for this module.
logger = logging.getLogger(__name__)

def home(request):
    """
    Finds the page marked as the 'homepage' in the database and renders it.
    If no homepage is set, it displays a default view.
    """
    logger.info(f"Homepage requested by user: {request.user.username or 'Anonymous'}")

    homepage = None
    try:
        homepage = Page.objects.filter(is_homepage=True, status='published').latest('updated_at')
        logger.debug(f"Serving homepage: '{homepage.title}' (ID: {homepage.id})")

    except Page.DoesNotExist:
        # This is a configuration warning, not an error. The site still works.
        logger.warning("No published page has been configured as the homepage. Serving a placeholder.")
        # The template itself handles displaying a user-friendly message.
        
    except Exception as e:
        # Catch any other unexpected database or logic errors.
        logger.error(
            f"An unexpected error occurred while fetching the homepage.",
            exc_info=True # Include the full traceback for debugging.
        )
        # In this case, homepage remains None, and the template will show a message.
        # A more robust solution might render a 500 error page.

    context = {
        'page': homepage,
    }

    return render(request, 'pages/page_detail.html', context)