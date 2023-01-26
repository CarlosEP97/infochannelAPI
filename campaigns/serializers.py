#serializer
from rest_framework import serializers
#models
# from django.contrib.auth.models import User
from .models import Campaigns,Timelines,Playlist,AddFiles
from django.db.models import F


import random
import string


class CampaignsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Campaigns
        ordering = ('campaign_name',)
        exclude = ('id',)


class UpdateCampaignsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Campaigns
        ordering = ('campaign_name',)
        exclude = ('id', 'created_date', 'last_update', 'screen_orientation', 'width', 'height')


''''timelines'''

class TimelinesOnSerializers(serializers.ModelSerializer):
    class Meta:
        model = Timelines
        fields = '__all__'
        read_only_fields = ('campaign',)

class TimelinesOffSerializers(serializers.ModelSerializer):
    class Meta:
        model = Timelines
        exclude = ('date_start', 'date_end', 'play_options', 'day_options',)
        read_only_fields = ('campaign',)


class TimelineCreateSerializer(serializers.ModelSerializer):
    timeline_name = serializers.CharField(max_length=100, default='default')

    class Meta:
        model = Timelines
        fields = ('timeline_name',)

    def create(self, validated_data):
        campaign = self.context['campaign']
        count_timelines = campaign.timelines_set.count()
        t = Timelines.objects.create(campaign=campaign, timeline_name=self.validated_data.get('timeline_name'),
                                     position=count_timelines)
        p = Playlist.objects.create(timelines=t, width=campaign.width, height=campaign.height)
        return t


class TimelinePositionUpdate(serializers.ModelSerializer):
    position = serializers.IntegerField()

    class Meta:
        model = Timelines
        fields = ('position',)

    def update(self, instance, validate_data):
        pv = instance.position
        np = validate_data.get('position', pv)
        c = self.context['campaign']
        if instance.position < np:
            instance.position = np
            c_timelines = c.timelines_set.filter(position__lte=instance.position).exclude(pk=instance.pk).values('pk')[
                           pv:]
            timelines = c.timelines_set.filter(pk__in=c_timelines)
            timelines.update(position=F('position') - 1)
            instance.save()
        elif instance.position > np:
            instance.position = np
            c_timelines = c.timelines_set.filter(position__gte=instance.position).exclude(pk=instance.pk)[:pv - np]
            timelines = c.timelines_set.filter(pk__in=c_timelines)
            timelines.update(position=F('position') + 1)
            instance.save()
        return instance


''''layouts'''


class PlaylistSerializer(serializers.ModelSerializer):
    resource_num = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        read_only_fields = ('created_at', 'last_update')
        exclude = ('resources', 'timelines', 'random_order')

    # def validate(self, attrs):
    #     width = attrs['width']
    #     height = attrs['height']
    #     top = attrs['top']
    #     left = attrs['left']
    #     if width or height or top or left > self.context['timeline'].width and self.context['timeline'].height:
    #         raise serializers.ValidationError('....')

    def get_resource_num(self, obj):
        return obj.resource_num
    def create(self, validated_data):
        timeline = self.context['timeline']
        playlist = Playlist.objects.create(timelines=timeline, **validated_data)
        return playlist




class PlaylistDetailSerializer(serializers.ModelSerializer):
    resources = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        read_only_fields = ('created_at', 'last_update',)
        exclude = ('timelines',)

    def get_resources(self, obj):
        add_files = AddFiles.objects.filter(playlist=obj)
        if obj.random_order:
            add_files = add_files.order_by('?')
        return PlaylistItems(add_files, many=True).data



class PlaylistItems(serializers.ModelSerializer):

    class Meta:
        model = AddFiles
        exclude = ('playlist',)


class PlaylistItemsSerializer(serializers.ModelSerializer):

    position = serializers.IntegerField()
    duration = serializers.DurationField()

    class Meta:
        model = AddFiles
        fields = ('position','duration',)

    def update(self, instance, validate_data):
        di = instance.duration
        pv = instance.position
        np = validate_data.get('position',pv)
        p = self.context['playlist']
        if instance.position < np:
            instance.position = np
            file_include = p.addfiles_set.filter(position__lte=instance.position).exclude(pk=instance.pk).values('pk')[pv:]
            file = p.addfiles_set.filter(pk__in=file_include)
            file.update(position=F('position') - 1)
            instance.save()
        elif instance.position > np:
            instance.position = np
            file_include = p.addfiles_set.filter(position__gte=instance.position).exclude(pk=instance.pk)[:pv-np]
            file = p.addfiles_set.filter(pk__in=file_include)
            file.update(position=F('position') + 1)
            instance.save()
        else:
            if instance.position == np:
                instance.duration = validate_data.get('duration', di)
                instance.save()

        return instance

