from django.shortcuts import render
from .models import Image

def gallery_view(request):
    images = Image.objects.all().order_by('-uploaded_at')
    return render(request, 'gallery/gallery.html', {'images': images})