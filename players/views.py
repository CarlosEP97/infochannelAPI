# models
from .models import Player
from django.contrib.auth.models import User
# serializers
from .serializers import PlayerSerializer, updatePlayerSerializer
# views
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
# filters
from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend
# auth
from .permissions import IsPlayerOwner
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet


class Playerlist(generics.ListCreateAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^name', 'status']
    ordering = ('start_time',)
    ordering_fields = ('status',)

    def get_queryset(self):
        user = self.request.user
        try:
            if user:
                return user.player_set.all().filter(status=True)
        except EmptyResultSet as e:
            return Response({"error": e}, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()
            if serializer:
                return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated | IsPlayerOwner]

    # def get_permissions(self):
    #     """Assign permission based on action."""
    #     permissions = [IsAuthenticated,IsPlayerOwner]
    #     return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on request.method."""
        if self.request.method in ['PUT', 'PATCH']:
            return updatePlayerSerializer
        return PlayerSerializer

    def get_object(self):
        user = self.request.user
        if user:
            player = user.player_set.get(pk=self.kwargs.get('pk'))
            if not player.status:
                return None
            return user.player_set.get(pk=self.kwargs.get('pk'))


    def update(self, request, *args, **kwargs):
        player = self.get_object()
        print(player)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(player, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        player = serializer.save()
        data = PlayerSerializer(player).data
        return Response(data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if instance:
            instance.status = False
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    ##permissions for update and destroy
    ## jwt auth


