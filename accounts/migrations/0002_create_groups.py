# accounts/migrations/XXXX_create_groups.py
from django.db import migrations

def create_user_groups(apps, schema_editor):
    # We get the Group and Permission models
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # --- EDITOR GROUP ---
    editor_group, created = Group.objects.get_or_create(name='Editor')
    if created:
        # We find the permissions we want to assign
        permissions = Permission.objects.filter(
            content_type__app_label__in=['blog'],
            codename__in=['add_post', 'change_post', 'delete_post', 'view_post', 
                          'add_postcategory', 'change_postcategory', 'delete_postcategory', 'view_postcategory']
        )
        editor_group.permissions.set(permissions)
        print("Editor group created and permissions assigned.")

    # --- PAGE MANAGER GROUP ---
    manager_group, created = Group.objects.get_or_create(name='Page Manager')
    if created:
        permissions = Permission.objects.filter(
            content_type__app_label__in=['pages', 'menus', 'widgets'],
            # Damos todos los permisos sobre estos modelos
        )
        manager_group.permissions.set(permissions)
        print("Page Manager group created and permissions assigned.")

    # --- COMMENT MODERATOR GROUP ---
    moderator_group, created = Group.objects.get_or_create(name='Comment Moderator')
    if created:
        permissions = Permission.objects.filter(
            content_type__app_label__in=['blog', 'contact'],
            codename__in=['change_comment', 'delete_comment', 'view_comment',
                          'change_contactmessage', 'delete_contactmessage', 'view_contactmessage']
        )
        moderator_group.permissions.set(permissions)
        print("Comment Moderator group created and permissions assigned.")

    # Add more groups like Administrator, Author here...

class Migration(migrations.Migration):

    dependencies = [
        # Depende de la migración anterior de la app 'accounts'
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_user_groups),
    ]