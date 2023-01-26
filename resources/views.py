from .models import Resource
from django.contrib.auth.models import User
# serializers
from .serializers import ResourceSerializer,CreateResourceSerializer
from rest_framework import generics

from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status
# filters
from rest_framework import filters
# auth
from rest_framework.permissions import IsAuthenticated
from .permissions import IsResourceOwner
#exceptions
from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet
#urls
from django.http import HttpResponseRedirect
from django.urls import reverse


class ResourcesList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^name', 'type_of_file']
    ordering = ('upload_date',)
    ordering_fields = ('upload_date', 'files')

    def get_serializer_class(self):
        """Return serializer based on method."""
        if self.request.method == 'GET':
            return ResourceSerializer
        return CreateResourceSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            if user:
                return Resource.objects.by_user_id(user)
        except EmptyResultSet:
            return None

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()
            if serializer:
                return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ResourcesRetrieve(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated | IsResourceOwner]
    serializer_class = ResourceSerializer

    def get_object(self):
        user = self.request.user
        try:
            if user:
                resource = user.resource_set.get(pk=self.kwargs.get('pk'))
                return resource
        except ObjectDoesNotExist:
            resource = None
            return resource

    def put(self, request, *args, **kwargs):
        resource = self.get_object()
        serializer = self.serializer_class(resource, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)



class ResourcesDestroy(generics.DestroyAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated | IsResourceOwner]

    # MULTIPLE DELETES filter by url
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        pk_ids = [int(pk) for pk in request.data.get('pk_ids', None).split(',')]
        if pk_ids and user:
            user.resource_set.filter(pk__in=pk_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FilesDownload(generics.RetrieveAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated | IsResourceOwner]

    def get_object(self):
        user = self.request.user.id
        pk = self.kwargs.get('pk',None)
        if user:
            return Resource.objects.by_user_resource(user, pk)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        file_handle = instance.files.open()
        # send file
        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = instance.files.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % instance.files.name
        return response