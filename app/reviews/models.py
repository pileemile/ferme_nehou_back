from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError

from app.customers.models import CustomerModel
from app.reservation.models import Reservation
from app.rooms.models import RoomModel


class Review(models.Model):
    client = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE)
    reservation = models.OneToOneField('reservation.Reservation', on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        unique_together = [['client', 'room', 'reservation']]

    def __str__(self):
        return f"Avis de {self.client.email} pour la chambre {self.room.name} (Réservation {self.reservation.id})"

    def clean(self):
        errors = {}
        if self.rating < 1 or self.rating > 5:
            errors['rating'] = "la note doit être comprise entre 1 et 5"

        has_validation_reservation = Reservation.objects.filter(
            client = self.client,
            room = self.room,
            status__in=['pending', 'confirmed']
        ).exists()

        if not has_validation_reservation:
            errors['client'] = "Vous devez avoir une réservation validée pour laisser un avis sur cette chambre."
        if self.reservation:
            if self.reservation.client != self.client:
                errors['reservation'] = "Cette réservation n'appartient pas ce client"
            if self.reservation.room != self.room:
                errors['reservation'] = "Cette réservation ne concerne pas cette chambre"
            if self.reservation.status not in ['confirmed', 'completed']:
                errors['reservation'] = "La réservation doit être confirmée ou terminée pour laisser un avis"
            if self.pk:
                existing_reviews = Review.objects.filter(
                    reservation = self.reservation
                ).exclude(pk=self.pk).exists()
            else:
                existing_reviews = Review.objects.filter(
                    reservation = self.reservation
                ).exists()
            if existing_reviews:
                errors['reservation'] = "un avis existe déjà pour cette réservation"
        if errors:
            raise ValidationError(errors)
    def save(self, *args, **kwargs):
        self.full_clean()
        super.save(*args, **kwargs)