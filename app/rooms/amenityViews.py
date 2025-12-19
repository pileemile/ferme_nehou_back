from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.permissions import IsAdminUser
from app.rooms.models import AmenityModel
from app.rooms.serializers import AmenitySerializer


class AmenityViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = [IsAdminUser]
    serializer_class = AmenitySerializer
    def get_queryset(self):
        return AmenityModel.objects.all()