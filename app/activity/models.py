from django.db import models

def activity_photo_path(instance, filename):
    return f'activity_photos/{instance.name.lower().replace(" ", "_")}/{filename}'


class Activity(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)
    photo = models.ImageField(upload_to=activity_photo_path, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)