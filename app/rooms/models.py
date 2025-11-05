from django.db import models

class RoomModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    capacity = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=7, decimal_places=2)
    available = models.BooleanField(default=True)
    main_photo = models.ImageField(upload_to='room_photos/', blank=True, null=True)