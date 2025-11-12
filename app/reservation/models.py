from django.db import models

from app.customers.models import CustomerModel
from app.rooms.models import RoomModel


class Reservation(models.Model):
    client = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, related_name='reservations')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guest_count = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2)