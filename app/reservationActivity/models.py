from django.db import models

from app.activity.models import Activity
from app.reservation.models import Reservation


class ReservationActivity(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='activities')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)