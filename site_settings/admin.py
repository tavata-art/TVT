# File: site_settings/admin.py
from django.contrib import admin
from solo.admin import SingletonModelAdmin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin, TabbedTranslationAdmin):
    """
    Admin for the SiteConfiguration singleton model.
    We keep it simple and let solo and modeltranslation handle the rendering.
    """
    # No 'fields' or 'fieldsets'. Let the libraries do their job.
    pass