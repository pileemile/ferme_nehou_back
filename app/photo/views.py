from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.permissions import IsAdminOrReadOnly
from app.photo.models import Photo
from app.photo.serializers import SerializerPhoto


class PhotoViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SerializerPhoto
    def get_queryset(self):
        return Photo.objects.all()