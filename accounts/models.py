# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.templatetags.static import static 

class Profile(models.Model):
    """
    Extends Django's base User model to include additional user information,
    such as a display name, avatar, and bio.
    """
    
    # --- Avatar Choices Enumeration ---
    # This provides a user-friendly way to select a default avatar.
    class AvatarChoice(models.TextChoices):
        PRIVATE = 'images/avatars/default_private.png', _("Don't specify")
        FEMALE = 'images/avatars/default_female.png', _('Female')
        MALE = 'images/avatars/default_male.png', _('Male')
        NONBINARY = 'images/avatars/default_nonbinary.png', _('Non-binary')

    # --- Core Relationship ---
    # A One-to-One link to Django's built-in User model.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # --- Identity & Contact Fields ---
    display_name = models.CharField(
        max_length=150, 
        blank=True, 
        verbose_name=_("Display Name"),
        help_text=_("Your full name or a nickname, which will be shown publicly.")
    )
    public_email = models.EmailField(
        blank=True, 
        verbose_name=_("Public Email"),
        help_text=_("An email address you don't mind sharing publicly for contact.")
    )
    website_url = models.URLField(
        max_length=255, 
        blank=True, 
        verbose_name=_("Website URL")
    )

    # --- Profile Information Fields ---
    location = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name=_("Location")
    )
    bio = models.TextField(
        blank=True, 
        verbose_name=_("Biography")
    )
    
    # --- Avatar Fields ---
    avatar = models.ImageField(
        upload_to='avatars/', 
        default='images/avatars/default_private.png', 
        verbose_name=_("Avatar")
    )
    default_avatar_choice = models.CharField(
        max_length=100,
        choices=AvatarChoice.choices,
        default=AvatarChoice.PRIVATE,
        verbose_name=_("Default Avatar Preference")
    )

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def get_avatar_url(self):
        """
        Returns the correct avatar URL, handling all cases:
        1. User has uploaded a custom avatar.
        2. User is using a default avatar.
        3. The avatar field is somehow empty/null (fallback).
        """
        try:
            # First, check if the avatar field has a file associated with it.
            # Accessing .url will fail if there is no file.
            if self.avatar and self.avatar.url:
                # To be 100% sure it's not just pointing to the default text path...
                default_path = self._meta.get_field('avatar').get_default()
                if self.avatar.name == default_path:
                    # It's a new user, pointing to the default. Return the static path.
                    return static(default_path)
                else:
                    # It's a custom uploaded image. Return its media path.
                    return self.avatar.url
        except ValueError:
            # This catches the "The 'avatar' attribute has no file associated with it." error
            pass # Continue to the fallback below

        # Fallback for any other case: return the default static path.
        return static('images/avatars/default_private.png')
        
    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_display_name(self):
        """
        Returns the user's preferred display name, with fallbacks.
        Order of preference: Profile's display_name -> User's full_name -> User's username.
        """
        return self.display_name or self.user.get_full_name() or self.user.username


# --- Django Signal to Automate Profile Creation ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a Profile when a new User is created.
    """
    if created:
        # Simply create the profile. Django will handle the default avatar.
        Profile.objects.create(user=instance)

    # This part ensures that if you save a User, its related Profile
    # is also saved, which can be useful for other signals.
    if hasattr(instance, 'profile'):
        instance.profile.save()