# core/templatetags/url_utils.py
from django import template

register = template.Library()

@register.simple_tag
def get_translated_url(obj, language_code):
    """
    Calls the get_absolute_url_for_language method on a given object
    and returns its result.
    Assumes the object has a method named 'get_absolute_url_for_language'.
    """
    if hasattr(obj, 'get_absolute_url_for_language'):
        return obj.get_absolute_url_for_language(language_code)
    # Fallback to current object's URL if method not found
    return obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else '#'