from django.utils import timezone
from rest_framework import permissions
from rest_framework.permissions import BasePermission

from app.reservation.models import Reservation
from app.utils.customers import get_customer_for_user

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        customer = get_customer_for_user(request.user)
        return customer is not None and obj.client_id == customer.id

class IsReservationOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        customer = get_customer_for_user(request.user)
        return customer is not None and obj.client_id == customer.id

class CanReviewReservation(permissions.BasePermission):

    message = "Vous devez avoir éffectué une réservation pour cette chambre avant de laisser un avis"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False

        if request.method != 'POST':
            return request.user.is_staff

        room_id = request.data.get('room')

        if not room_id:
            return False

        customer = get_customer_for_user(request.user)
        if customer is None:
            return False

        has_valid_reservation = Reservation.objects.filter(
            client=customer,
            room_id = room_id,
            status__in=['confirmed', 'completed'],
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
