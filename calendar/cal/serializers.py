from rest_framework import serializers

from cal import models


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Event
        fields = '__all__'