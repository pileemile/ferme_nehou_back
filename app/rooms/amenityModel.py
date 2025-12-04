from django.db import models

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