from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.reservationActivity.models import ReservationActivity
from app.reservationActivity.serializers import SerializerReservationActivity


class ReservationActivityViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = SerializerReservationActivity
    def get_queryset(self):
        return ReservationActivity.objects.all()