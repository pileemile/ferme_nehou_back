from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.reservation.models import Reservation
from app.reservation.serializers import ReservationSerializer


class ReservationViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = ReservationSerializer
    def get_queryset(self):
        return Reservation.objects.all()