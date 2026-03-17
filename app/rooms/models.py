from django.db import models

from app.validators import validate_capacity, validate_price


class AmenityModel(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)

    '''
    Tu pourras ensuite créer des amenities comme :
    | name         | icon                       |
    | ------------ | -------------------------- |
    | Wi-Fi        | fa-solid fa-wifi           |
    | Jacuzzi      | fa-solid fa-hot-tub-person |
    | TV           | fa-solid fa-tv             |
    | Kitchen      | fa-solid fa-kitchen-set    |
    | Free Parking | fa-solid fa-square-parking |

    '''

def room_main_photo_path(instance, filename):
    return f'room_photos/chambre-{instance.id}/main_{filename}'

class RoomModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    capacity = models.IntegerField(validators=[validate_capacity])
    price_per_night = models.DecimalField(max_digits=7,decimal_places=2,validators=[validate_price] )
    available = models.BooleanField(default=True)
    main_photo = models.ImageField(upload_to=room_main_photo_path, blank=True, null=True)
    amenities = models.ManyToManyField(AmenityModel, related_name='rooms', blank=True)
