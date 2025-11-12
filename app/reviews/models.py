from django.db import models

from app.customers.models import CustomerModel
from app.rooms.models import RoomModel


class Review(models.Model):
    client = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)