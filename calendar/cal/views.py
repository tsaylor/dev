from rest_framework import viewsets
from rest_framework import permissions

from cal import models, serializers


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Event.objects.all().order_by('-start_date')
    serializer_class = serializers.EventSerializer
    permission_classes = [permissions.IsAuthenticated]