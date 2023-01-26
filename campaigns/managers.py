from django.db import models

class CampaignsQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)

    def campaigns_id(self, pk):
        return self.filter(pk=pk)

    def user_campaigns(self, user_id, pk):
        return self.get(user_id=user_id, pk=pk)


class CampaignsManager(models.Manager):
    def get_queryset(self):
        return CampaignsQuerySet(self.model, using=self._db)

    def by_user_id(self, user_id):
        return self.get_queryset().by_user(user_id)

    def by_campaigns_id(self, pk):
        return self.get_queryset().campaigns_id(pk)

    def by_user_campaigns(self, user_id, pk):
        return self.get_queryset().user_campaigns(user_id, pk)


""""TIMELINES"""


class TimelinesQuerySet(models.QuerySet):
    def by_campaign(self, campaigns_id):
        return self.filter(campaign_id=campaigns_id)

    def timeline_id(self, pk):
        return self.filter(pk=pk)

    def timeline_campaigns(self, campaign_id, pk):
        return self.get(campaign_id=campaign_id, pk=pk)

    def timeline_obj(self, pk):
        return self.get(pk=pk)


class TimelinesManager(models.Manager):
    def get_queryset(self):
        return TimelinesQuerySet(self.model, using=self._db)

    def by_campaign_id(self, campaigns_id):
        return self.get_queryset().by_campaign(campaigns_id)

    def by_timeline_id(self, pk):
        return self.get_queryset().timeline_id(pk)

    def by_timeline_campaigns(self, campaign_id, pk):
        return self.get_queryset().timeline_campaigns(campaign_id, pk)

    def by_timeline_obj(self, pk):
        return self.get_queryset().timeline_obj(pk)


class PlaylistQuerySet(models.QuerySet):

    def playlist_id(self, pk):
        return self.get(pk=pk)

    def timeline_playlist(self, timeline_id, pk):
        return self.get(timelines_id=timeline_id, pk=pk)

    def timeline_playlists(self, timeline_id):
        return self.filter(timelines_id=timeline_id)


class PlaylistManager(models.Manager):
    def get_queryset(self):
        return PlaylistQuerySet(self.model, using=self._db)

    def by_playlist_id(self, pk):
        return self.get_queryset().playlist_id(pk)

    def by_timeline_playlist(self, timeline_id, pk):
        return self.get_queryset().timeline_playlist(timeline_id, pk)

    def by_timeline_playlists(self,timeline_id ):
        return self.get_queryset().timeline_playlists(timeline_id)