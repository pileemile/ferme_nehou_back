from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from app.customers.models import CustomerModel
from app.rooms.models import RoomModel


class Reservation(models.Model):

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('canceled', 'Annulée'),
        ('completed', 'Terminée')
    ]

    client = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, related_name='reservations')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guest_count = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES ,default='pending')
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Reservation {self.id} - {self.room.name} - {self.client.email}"

    def clean(self):
        errors = {}

        if self.check_out_date <= self.check_in_date:
            errors['check_out_date'] = "la date de départ doit être après la date d'arriver"

        if self.guest_count > self.room.capacity:
            errors['guest_count'] = f"le nombre de personnes ({self.guest_count}) dépasse la capacité de la chambre ({self.room.capacity})"

        if self.check_in_date < timezone.now().date():
            errors['check_in_date'] = "la date d'arriver ne peut pas être dans le passé"

        if self.pk:
            overlapping = Reservation.objects.filter(
                room=self.room,
                status__in=['pending', 'confirmed'],
            ).exclude(pk=self.pk)
        else:
            overlapping = Reservation.objects.filter(
                room=self.room,
                status__in=['pending', 'confirmed']
            )
        overlapping = overlapping.filter(
            check_in_date__lte=self.check_out_date,
            check_out_date__gte=self.check_in_date
        )

        if overlapping.exists():
            errors['check_in_date'] = "Cette est déjà réserver a cette date"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.check_in_date and self.check_out_date and self.room:
            nights =(self.check_out_date - self.check_in_date).days
            self.total_price = nights * self.room.price_per_night
        self.full_clean()
        super().save(*args, **kwargs)

    def get_number_of_nights(self):
        return (self.check_out_date - self.check_in_date).days

    def can_be_canceled(self):
        return self.status in ['pending', 'confirmed'] and self.check_in_date > timezone.now().date()

    def can_be_completed(self):
        return self.status == 'pending'