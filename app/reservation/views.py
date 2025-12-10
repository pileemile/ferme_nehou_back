from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
        return Reservation.objects.all().select_related('customer', 'room')

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        reservation = self.get_object()

        if not reservation.can_be_confirmed:
            return Response({
                'error' : 'Cette réservation ne peut pas être confirmer'},
                status= status.HTTP_400_BAD_REQUEST
            )
        reservation.status = 'confirmed'
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        reservation = self.get_object()

        if reservation.status != 'confirmed':
            return Response(
                {'error' : 'Seules les réservation confirmée peuvent être terminées'},
                status= status.HTTP_400_BAD_REQUEST
            )

        if reservation.check_out_date > timezone.now().date():
            return Response(
                {'error' : 'La réservation n\'est pas encore terminée'},
                status= status.HTTP_400_BAD_REQUEST
            )

        reservation.status = 'completed'
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
