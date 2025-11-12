from django.db import models

from app.rooms.models import RoomModel


class Photo(models.Model):
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, null=True, blank=True)
    file_url = models.URLField()
    description = models.TextField(blank=True)