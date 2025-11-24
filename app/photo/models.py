from django.db import models

from app.rooms.models import RoomModel


def room_photo_path(instance, filename):
    return f'room_photos/chambre-{instance.room.id}/photo_{filename}'

class Photo(models.Model):
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, null=True, blank=True, related_name='photos')
    file = models.ImageField(upload_to=room_photo_path, null=True, blank=True)
    description = models.TextField(blank=True)
