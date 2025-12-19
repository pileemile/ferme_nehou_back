from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from app.reservation.models import Reservation


@receiver(post_save, sender=Reservation)
def update_room_availability_on_save(sender, instance, **kwargs):
    room = instance.room

    active_reservations = Reservation.objects.filter(
        room = room,
        status__in=['pending', 'confirmed'],
        check_out_date=timezone.now().date()
    ).exists()
    room.is_available = not active_reservations
    room.save(update_fields=['available'])

@receiver(post_delete, sender=Reservation)
def update_room_availability_on_delete(sender, instance, **kwargs):
    room = instance.room

    active_reservations = Reservation.objects.filter(
        room = room,
        status__in=['pending', 'confirmed'],
        check_out_date=timezone.now().date()
    ).exists()
    room.is_available = not active_reservations
    room.save(update_fields=['available'])