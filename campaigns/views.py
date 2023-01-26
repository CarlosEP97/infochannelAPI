from .models import Campaigns, Timelines, Playlist, AddFiles
from resources.models import Resource
from .serializers import CampaignsSerializer, UpdateCampaignsSerializer, TimelinesOnSerializers,TimelinesOffSerializers,TimelineCreateSerializer,\
    TimelinePositionUpdate,PlaylistSerializer,PlaylistDetailSerializer,PlaylistItemsSerializer
from rest_framework import generics,mixins
from django.db.models import Case,When
from django.db.models import F,Q,Count
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.filters import SearchFilter
#e#Exceptions
from django.core.exceptions import ObjectDoesNotExist , EmptyResultSet

# view for create campaign step by step
# 1 camping object create : name
# 2 screen orientation
# 3 resolution
# 4 a timeline with the initial resolution
# 4.1 layout with that resolution
# 4.2 playlist with the layout

# them LIST,DETAIL,UPDATE,DELETE

class Campaign(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CampaignsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^campaign_name','user__username']
    ordering = ('created_date',)
    ordering_fields = 'last_update'


    def get_queryset(self):
        user = self.request.user
        try:
            if user:
                return Campaigns.objects.by_user_id(user)
        except EmptyResultSet:
            return None


    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()
            if serializer:
                return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CampaignRetrieve(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CampaignsSerializer

    def get_object(self):
        user = self.request.user.id
        try:
            if user:
                campaign = Campaigns.objects.by_user_campaigns(user,self.kwargs.get('pk',None))
                return campaign
        except ObjectDoesNotExist:
            return None

    def put(self, request, *args, **kwargs):
        if not self.get_object():
            return None
        campaign = self.get_object()
        serializer = UpdateCampaignsSerializer(campaign, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = CampaignsSerializer(campaign).data
        return Response(data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class CampaignTimelines(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TimelinesOffSerializers

    def get_queryset(self):
        user = self.request.user.id
        campaign_pk = self.kwargs.get('pk', None)
        try:
            if user and campaign_pk:
                campaign = Campaigns.objects.by_user_campaigns(user, campaign_pk)
                campaign_timelines = campaign.timelines_set.all()
                return campaign_timelines
        except EmptyResultSet:
            return None

    def get_object(self):
        user = self.request.user.id
        campaign_pk = self.kwargs.get('pk', None)
        try:
            if user and campaign_pk:
                campaign = Campaigns.objects.by_user_campaigns(user, campaign_pk)
                return campaign
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        campaign_timelines = self.get_queryset()
        data = self.serializer_class(campaign_timelines, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = TimelineCreateSerializer(data=request.data,
                                              context={'campaign': self.get_object()})
        serializer.is_valid(raise_exception=True)
        timeline = serializer.save()
        data = self.serializer_class(timeline).data
        return Response(data, status=status.HTTP_200_OK)


    def put(self, request, *args, **kwargs):
        """Update timeline position """
        timeline = Timelines.objects.by_timeline_obj(self.request.data.get('pk', None))
        print(request.data)
        serializer = TimelinePositionUpdate(timeline, data=request.data, partial=True,
                                            context={'campaign': self.get_object()})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        campaign = self.get_object()
        campaign_get = Timelines.objects.by_timeline_campaigns(campaign,self.request.data.get('pk', None))
        timelines = campaign.timelines_set.filter(position__gte=campaign_get.position).exclude(pk=campaign_get.pk)
        campaign_get.delete()
        timelines.update(position=F('position') - 1)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TimelineDetail(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            if self.request.user:
                timeline = Timelines.objects.by_timeline_obj(self.kwargs.get('pk'))
                return timeline
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        timeline = self.get_object()
        campaign = timeline.campaign
        if campaign.playback_mode is True:
            serializer = TimelinesOnSerializers(timeline)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = TimelinesOffSerializers(timeline)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """""restrict the date for update hacer esto"""
        timeline = self.get_object()
        campaign = timeline.campaign
        if campaign.playback_mode is True:
            serializer = TimelinesOnSerializers(timeline, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = TimelinesOffSerializers(timeline, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class TimelinesLayouts(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = PlaylistSerializer

    def get_object(self):
        try:
            if self.request.user:
                timeline = Timelines.objects.by_timeline_obj(self.kwargs.get('pk'))
                return timeline
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        timeline = self.get_object()
        layouts = timeline.playlist_set.all()
        serializer = self.serializer_class(layouts, many=True)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                        context={'timeline': self.get_object()})
        serializer.is_valid(raise_exception=True)
        layout = serializer.save()
        data = self.serializer_class(layout).data
        return Response(data, status=status.HTTP_200_OK)


class Layouts(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            if self.request.user:
                layout = Playlist.objects.by_playlist_id(self.kwargs.get('pk'))
                return layout
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        layout = self.get_object()
        serializer = PlaylistDetailSerializer(layout)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        layout = self.get_object()
        serializer = PlaylistDetailSerializer(layout, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        layout = self.get_object()
        layout.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) # delete must be in timeline if timeline layout is < 1 can delete the playlist


class PlaylistAddfile(mixins.UpdateModelMixin, generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = PlaylistItemsSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            if user:
                print(self.request.data)
                pk_ids = [int(pk) for pk in self.request.data.get('pk_ids', None).split(',')]
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_ids)])
                print(preserved)
                resource = user.resource_set.filter(pk__in=pk_ids).order_by(preserved)
                return resource
        except EmptyResultSet:
            return None

    def get_object(self):
        user = self.request.user.pk
        try:
            if user:
                playlist = Playlist.objects.by_playlist_id(self.kwargs.get('playlist_id'))
                # print(list(playlist.addfiles_set.all().values('resource','position')))
                return playlist
        except ObjectDoesNotExist:
            return None

    def post(self,request,*args,**kwargs):
        user = self.request.user
        if user:
            playlist = self.get_object()
            count_playlist = playlist.resources.count()
            resource = self.get_queryset()
            add_resources = list()
            for i, resource_id in enumerate(resource, start=count_playlist):
                resource1 = Resource.objects.get(pk=resource_id.pk)
                # AddFiles.objects.bulk_create([AddFiles(resource=resource1, playlist=playlist, position=i)])
                addfiles = AddFiles(resource=resource1, playlist=playlist, position=i)
                add_resources.append(addfiles)
            AddFiles.objects.bulk_create(add_resources)
        data = PlaylistDetailSerializer(self.get_object()).data
        data['message'] = f'file {self.get_queryset()} added to playlist {self.get_object()}'
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """"limit for move a file hacer esto"""
        playlist = self.get_object()
        file = playlist.addfiles_set.get(pk=self.request.data.get('resource_id'))
        #form data
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(file, data=request.data, partial=True, context={"playlist": playlist})
        print(self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = PlaylistDetailSerializer(playlist).data
        return Response(data, status=status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs):
        p = self.get_object()
        file = p.addfiles_set.get(pk=self.request.data.get('resource_id'))
        files = p.addfiles_set.filter(position__gte=file.position).exclude(pk=file.pk)
        file.delete()
        files.update(position=F('position') - 1)
        return Response(status=status.HTTP_204_NO_CONTENT)
#

#
class RandomOrder(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = PlaylistItems

    def get_object(self):
        user = self.request.user.pk
        try:
            if user:
                playlist = Playlist.objects.by_playlist_id(self.kwargs.get('playlist_id'))
                return playlist
        except ObjectDoesNotExist:
            return None

    def put(self, request, *args, **kwargs):
        playlist = self.get_object()
        if playlist.random_order is False:
            playlist.random_order = True
            playlist.save()
        else:
            playlist.random_order = False
            playlist.save()
        data = PlaylistDetailSerializer(playlist).data
        return Response(data, status=status.HTTP_200_OK)



class SearchPlaylist(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]


    def get(self,request,*args,**kwargs):
        sf = SearchFilter()
        # print(sf.search_param) = search in postman
        subject = request.query_params[sf.search_param]
        # print(sf.filter_queryset())
        # print(subject1)
        # subject = self.request.query_params.get('search_param',None)
        # total = Playlist.objects.filter(name__search = 'default')

        print(subject)
        if subject is not None:
            vector = SearchVector('name', weight='A')
            query = SearchQuery(subject)
            # p = Playlist.objects.annotate(search=vector).filter(search=query)
            # p = Playlist.objects.annotate(rank=SearchRank(vector,query)).annotate(resource_num = Count(F('resources'))).order_by('-resource_num')
            # p = Playlist.objects.annotate(rank=SearchRank(vector, query),resource_num = Count(F('resources'))).filter(name__icontains=subject).order_by('-rank')
            p = Playlist.objects.filter(Q(name=subject) | Q(resources__isnull=False)).annotate(
                rank=SearchRank(vector, query), resource_num=Count('resources')).order_by('-rank')
            print(vars(p[0]))
            # print(p)
            data = PlaylistSerializer(p,many=True)
        return Response(data.data,status=status.HTTP_200_OK)
