from django.contrib import admin
from .models import Player


@admin.register(Player)
class players(admin.ModelAdmin):
    list_display = ('pk', 'user', 'category', 'name', 'status', 'start_time', 'last_update')
    # list_display_links = ('pk', 'user',)
    # list_editable = ()

    search_fields = (
        'name',
        'user__email',
        'user__username',
    )

    list_filter = (
        'category',
        'status',
        'user__is_active',
        'user__is_staff',
    )
