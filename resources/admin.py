from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Resource


# class AddFiles1(admin.TabularInline):
#
#     model = Playlist.resources.through


@admin.register(Resource)
class resources(admin.ModelAdmin):
    """Resource."""

    list_display = ('pk', 'user', 'name', 'files', 'type_of_file', 'upload_date')
    list_display_links = ('pk',)
    # list_editable = ()

    search_fields = (
        'name',
        'user__email',
        'user__username',
    )

    list_filter = (
        'type_of_file',
        'user__is_active',
        'user__is_staff',
    )

