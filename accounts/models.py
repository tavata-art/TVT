# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
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
    is_trusted_commenter = models.BooleanField(
        default=False,
        verbose_name=_("Is a Trusted Commenter?"),
        help_text=_("If checked, comments are automatically approved.")
    )
    is_listed_publicly = models.BooleanField(
        default=False, # consider False for new registrations.
                       # We will make this configurable in the signup process.
        verbose_name=_("List profile publicly?"),
        help_text=_("If checked, your profile will be visible in the public user directory.")
    )

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    # accounts/models.py
    def get_avatar_url(self):
        # Si el usuario ha subido un archivo, su nombre NO será una de las rutas por defecto.
        default_paths = [c[0] for c in self.AvatarChoice.choices]
        if self.avatar and self.avatar.name not in default_paths:
            return self.avatar.url

        # Si no, mostramos el avatar por defecto que el usuario haya elegido.
        return static(self.default_avatar_choice)
        
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