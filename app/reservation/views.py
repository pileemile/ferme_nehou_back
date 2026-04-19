from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.emails.service import EmailService
from app.notifications.services import NotificationService
from app.permissions import IsOwnerOrAdmin
from app.reservation.models import Reservation
from app.reservation.serializers import ReservationSerializer
from app.tasks import (
    send_admin_notification_async,
    send_reservation_confirmation_async,
)
from app.utils.customers import get_customer_for_user


class ReservationViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = Reservation.objects.select_related("client", "room")
        if self.request.user.is_staff:
            return queryset

        customer = get_customer_for_user(self.request.user)
        if customer is None:
            return Reservation.objects.none()
        return queryset.filter(client=customer)

    def perform_create(self, serializer):
        customer = get_customer_for_user(self.request.user)
        if customer is None:
            raise ValidationError(
                {"client": "Aucun profil client n'est associé à cet utilisateur."}
            )
        serializer.save(client=customer)

    def perform_update(self, serializer):
        reservation = self.get_object()
        serializer.save(client=reservation.client)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        reservation = self.get_object()

        if reservation.status != "pending":
            return Response(
                {"error": "Seules les réservations en attente peuvent être confirmées."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.status = "confirmed"
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        reservation = self.get_object()

        if reservation.status != "confirmed":
            return Response(
                {"error": "Seules les réservations confirmées peuvent être terminées."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reservation.check_out_date > timezone.now().date():
            return Response(
                {"error": "La réservation n'est pas encore terminée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.status = "completed"
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        reservation = Reservation.objects.select_related("client", "room").get(
            pk=response.data["id"]
        )

        EmailService.send_reservation_confirmation(reservation)
        EmailService.send_admin_new_reservation(reservation)
        send_reservation_confirmation_async.delay(reservation.id)
        send_admin_notification_async.delay(reservation.id)
        NotificationService.notify_reservation_confirmed(reservation)

        return response

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        reservation = self.get_object()

        if not reservation.can_be_canceled():
            return Response(
                {"error": "Cette réservation ne peut pas être annulée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.status = "canceled"
        reservation.save()

        days_before = (reservation.check_in_date - timezone.now().date()).days
        if days_before >= 7:
            refund_info = "vous serez remboursé intégralement"
        else:
            refund_info = "50% du montant vous sera remboursé"

        EmailService.send_reservation_cancelled(reservation, refund_info)
        NotificationService.notify_reservation_cancelled(reservation)

        serializer = self.get_serializer(reservation)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        old_reservation = self.get_object()
        old_dates = (old_reservation.check_in_date, old_reservation.check_out_date)
        old_guests = old_reservation.guest_count

        response = super().update(request, *args, **kwargs)
        reservation = Reservation.objects.select_related("client", "room").get(
            pk=response.data["id"]
        )

        changes = []
        if old_dates[0] != reservation.check_in_date or old_dates[1] != reservation.check_out_date:
            changes.append(
                f"Dates modifiées : {reservation.check_in_date.strftime('%d/%m/%Y')} - {reservation.check_out_date.strftime('%d/%m/%Y')}"
            )
        if old_guests != reservation.guest_count:
            changes.append(f"Nombre de voyageurs : {reservation.guest_count}")

        if changes:
            EmailService.send_reservation_modified(reservation, changes)

        return response
