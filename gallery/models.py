# File: gallery/models.py
from django.db import models
from django.urls import reverse # Import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override 
import logging

logger = logging.getLogger(__name__)

class Image(models.Model):
    """
    Represents an image in the gallery with a title and description.
    """
    # Title stores the image's name/description, translatable.
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    
    # Image file field. Images will be uploaded to the 'gallery/' subfolder in MEDIA_ROOT.
    image = models.ImageField(upload_to='gallery/', verbose_name=_("Image"))
    
    # NEW: Optional description for the image, translatable.
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Auto-added timestamp for when the image was uploaded.
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded at"))

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

    def __str__(self):
        # modeltranslation automatically returns the translated title.
        return self.title

    def get_absolute_url(self):
        """ Returns the URL to view this specific image's detail page. """
        # This will point to a dedicated view for the image itself.
        return reverse('gallery:image_detail', args=[self.pk]) 
    
    def get_absolute_url_for_language(self, language_code):
        with override(language_code):
            # El PK no cambia con el idioma, así que solo necesitamos el reverse en el contexto del idioma.
            return reverse('gallery:image_detail', args=[self.pk])