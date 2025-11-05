from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.activity.models import Activity
from app.activity.serializers import SerializerActivity


class ActivityViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = SerializerActivity
    def get_queryset(self):
        return Activity.objects.all()