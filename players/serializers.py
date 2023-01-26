#serializer
from rest_framework import serializers
#models
from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # type = serializers.HiddenField(default=)
    class Meta:
        model = Player
        fields = '__all__'
        # exclude = ('id',)
        read_only_fields = ('user', 'start_time', 'last_update','status','id')



class updatePlayerSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # type = serializers.HiddenField(default=)
    class Meta:
        model = Player
        fields = ('name', 'category','status','long','lat')
        read_only_fields = ('user', 'start_time', 'last_update')


