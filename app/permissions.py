from django.utils import timezone
from rest_framework import permissions

from app.reservation.models import Reservation
from app.rooms.models import RoomModel

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True


        return obj.client == request.user

class IsReservationOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.client == request.user

class CanReviewReservation(permissions.BasePermission):

    message = "Vous devez avoir éffectué une réservation pour cette chambre avant de laisser un avis"

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        if not request.user.is_authenticated:
            return False

        room_id = request.data.get('room')

        if not room_id:
            return False

        has_valid_reservation = Reservation.objects.filter(
            client = request.user,
            room_id = room_id,
            status='confirmed',
            check_out_date__lte=timezone.now().date()
        ).exists()

        return has_valid_reservation

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff