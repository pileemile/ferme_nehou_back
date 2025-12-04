from django.db import models


def room_main_photo_path(instance, filename):
    return f'room_photos/chambre-{instance.id}/main_{filename}'

class RoomModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    capacity = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=7, decimal_places=2)
    available = models.BooleanField(default=True)
    main_photo = models.ImageField(upload_to=room_main_photo_path, blank=True, null=True)
    amenities = models.ManyToManyField('AmenityModel', related_name='rooms', blank=True)
