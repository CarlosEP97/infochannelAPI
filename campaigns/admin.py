from django.contrib import admin
from .models import Campaigns,Timelines,Playlist,AddFiles


@admin.register(Campaigns)
class Campaigns(admin.ModelAdmin):
    """Resource."""

    list_display = ('pk', 'user', 'campaign_name', 'screen_orientation', 'width', 'height', 'playback_mode', 'created_date', 'last_update' )
    list_display_links = ('pk',)
    # list_editable = ()

    search_fields = (
        'campaign_name',
        'playback_mode',
        'user__username',
    )

    list_filter = (
        'screen_orientation',
        'playback_mode',
    )


@admin.register(Timelines)
class Timelines(admin.ModelAdmin):
    """Resource."""

    list_display = ('pk', 'timeline_name', 'position', 'date_start', 'date_end', 'play_options', 'day_options','get_campaign_name')
    list_display_links = ('pk',)


    search_fields = (
        'timeline_name',
        'date_start',
        'date_end',
    )

    list_filter = (
        'play_options',
        'position',
    )

    @admin.display(ordering='campaign__campaign_name', description='campaign name')
    def get_campaign_name(self, obj):
        return obj.campaign.campaign_name

@admin.register(Playlist)
class Playlist(admin.ModelAdmin):
    """Resource."""

    list_display = ('pk', 'name', 'created_at', 'last_update','top', 'left','width', 'height','z_index','get_timeline_name')
    list_display_links = ('pk',)
    # inlines = [AddFiles1]
    # list_editable = ()

    search_fields = (
        'name',
    )

    list_filter = (
        'name',
        'created_at',
        'last_update',
    )

    @admin.display(ordering='timelines__timeline_name', description='timeline name')
    def get_timeline_name(self, obj):
        return obj.timelines.timeline_name


@admin.register(AddFiles)
class AddFiles(admin.ModelAdmin):
    """Resource."""

    list_display = ('pk', 'playlist', 'resource', 'position')
    list_display_links = ('pk',)
    # list_editable = ()

    search_fields = (
        'Resource__name',
        'playlist__name',
    )

    list_filter = (
        'position',
    )
