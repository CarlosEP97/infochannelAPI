#serializer
from rest_framework import serializers
#models
from .models import Resource



class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource
        ordering = ('upload_date',)
        exclude = ('user',)
        read_only_fields = ('files', 'type_of_file', 'upload_date')


class CreateResourceSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Resource
        exclude = ('id',)
