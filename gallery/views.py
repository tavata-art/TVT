# File: gallery/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.html import strip_tags 
from django.utils.translation import get_language, activate, deactivate 

from site_settings.models import SiteConfiguration 
from blog.models import Post # For collecting featured images from posts
from pages.models import Page # For collecting featured images from pages (assuming it has featured_image)
from .models import Image # For images specifically in the gallery app
import logging

logger = logging.getLogger(__name__)

# Helper function to get a truncated description (remains the same)
def get_truncated_description(text, max_length=200):
    if not text:
        return ""
    # Ensure text is string-like before stripping tags
    stripped_text = strip_tags(str(text)) 
    if len(stripped_text) > max_length:
        return stripped_text[:max_length] + "..."
    return stripped_text

def gallery_view(request):
    """
    Collects all featured images from published Posts and Pages
    to display them in a unified gallery.
    """
    gallery_items_data = [] # This list will hold uniform dictionaries for the template
    current_lang = get_language() # Get current language for consistent data retrieval

    # --- Get all images from the gallery.Image model ---
    for img_obj in Image.objects.all():
        activate(current_lang)
        # Debugging: Check direct values from the model object
        _img_url = img_obj.image.url if img_obj.image else ''
        _detail_url = img_obj.get_absolute_url()
        _uploaded_at = img_obj.uploaded_at
        logger.debug(f"DEBUG Image (ID: {img_obj.pk}): URL={_img_url}, DetailURL={_detail_url}, UploadedAt={_uploaded_at}")

        gallery_items_data.append({
            'image_url': _img_url,
            'title': img_obj.title, # modeltranslation handles this
            'description': get_truncated_description(img_obj.description),
            'detail_url': _detail_url,
            'date': _uploaded_at, # Consistent key for sorting
            'type': 'Image'
        })
        deactivate()
    
    # --- Get featured images from blog.Post model ---
    posts_with_images = Post.objects.filter(
        status='published', 
        featured_image__isnull=False
    ).exclude(featured_image__exact='').order_by('-published_date')

    for post_obj in posts_with_images:
        activate(current_lang) 
        # Debugging: Check direct values from the model object
        _post_img_url = post_obj.featured_image.url if post_obj.featured_image else ''
        _post_detail_url = post_obj.get_absolute_url()
        _post_published_date = post_obj.published_date
        logger.debug(f"DEBUG Post (ID: {post_obj.pk}): URL={_post_img_url}, DetailURL={_post_detail_url}, PublishedDate={_post_published_date}")

        gallery_items_data.append({
            'image_url': _post_img_url,
            'title': post_obj.title, # modeltranslation handles this
            'description': get_truncated_description(post_obj.meta_description or post_obj.content), 
            'detail_url': _post_detail_url,
            'date': _post_published_date, # Consistent key for sorting
            'type': 'Post'
        })
        deactivate()

    # --- Get featured images from pages.Page model (if featured_image field exists) ---
    # To include pages, ensure pages.models.Page has a 'featured_image' field.
    # Otherwise, this part will be skipped or cause an error.
    try:
        pages_with_images = Page.objects.filter(
            status='published',
            featured_image__isnull=False
        ).exclude(featured_image__exact='').order_by('-updated_at') # Order pages by update date

        for page_obj in pages_with_images:
            activate(current_lang)
            # Debugging: Check direct values from the model object
            _page_img_url = page_obj.featured_image.url if page_obj.featured_image else ''
            _page_detail_url = page_obj.get_absolute_url()
            _page_updated_at = page_obj.updated_at
            logger.debug(f"DEBUG Page (ID: {page_obj.pk}): URL={_page_img_url}, DetailURL={_page_detail_url}, UpdatedAt={_page_updated_at}")
            
            gallery_items_data.append({
                'image_url': _page_img_url,
                'title': page_obj.title, # modeltranslation handles this
                'description': get_truncated_description(page_obj.meta_description or page_obj.content),
                'detail_url': _page_detail_url,
                'date': _page_updated_at, # Consistent key for sorting
                'type': 'Page'
            })
            deactivate()
    except Exception as e:
        logger.warning(f"Could not retrieve featured images from Pages: {e}. Ensure 'featured_image' field exists on Page model and it's properly configured.")


    # --- Sort the combined list by date (newest first) ---
    # We use a lambda function and a default value for 'date' key in case it's missing.
    gallery_items_data.sort(key=lambda x: x.get('date', x.get('uploaded_at', x.get('published_date', None) or x.get('updated_at', None))), reverse=True)
    
    # --- Apply Pagination --- (remains the same)
    try:
        site_config = SiteConfiguration.objects.get()
        # Make sure this setting is defined in SiteConfiguration, or use a fallback.
        gallery_items_per_page = site_config.gallery_items_per_page 
    except SiteConfiguration.DoesNotExist:
        gallery_items_per_page = 9 # Fallback value
        logger.warning("SiteConfiguration not found. Using default gallery pagination (9 items).")
    
    paginator = Paginator(gallery_items_data, gallery_items_per_page)
    page_number = request.GET.get('page')

    try:
        images_on_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        images_on_page = paginator.get_page(1)
    except EmptyPage:
        images_on_page = paginator.get_page(paginator.num_pages)
    
    logger.info(f"Gallery view accessed. Showing page {images_on_page.number} of {images_on_page.paginator.num_pages} images.")

    context = {
        'images': images_on_page # Passed to template as 'images'
    }

    return render(request, 'gallery/gallery_page.html', context)

# NEW: View for individual image detail
def image_detail_view(request, pk):
    """ 
    Displays details for a single image from the gallery. 
    This is a basic placeholder; will be styled in a template later.
    """
    image = get_object_or_404(Image, pk=pk) # Fetches the image by its primary key
    context = {'image': image}
    
    # We will create this template in the next step.
    return render(request, 'gallery/image_detail.html', context)