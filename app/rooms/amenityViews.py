from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.rooms.amenityModel import AmenityModel
from app.rooms.amenitySerializers import AmenitySerializer


class AmenityViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = AmenitySerializer
    def get_queryset(self):
        return AmenityModel.objects.all()