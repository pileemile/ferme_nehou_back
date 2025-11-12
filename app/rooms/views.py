from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.rooms.filter import RoomFilter
from app.rooms.models import RoomModel
from app.rooms.serializers import SerializerRooms


class RoomViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = SerializerRooms
    def get_queryset(self):
        return RoomModel.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter