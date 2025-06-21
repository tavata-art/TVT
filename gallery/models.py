from django.db import models
from django.utils.translation import gettext_lazy as _

class Image(models.Model):
    # Title is translatable with django-modeltranslation
    title = models.CharField(_("Title"), max_length=100)
    image = models.ImageField(_("Image"), upload_to='gallery/')
    uploaded_at = models.DateTimeField(_("Uploaded at"), auto_now_add=True)

    def __str__(self):
        # Always return the translated title
        return self.title