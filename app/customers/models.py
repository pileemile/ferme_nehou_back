from django.conf import settings
from django.db import models
from django.core.validators import EmailValidator
from app.validators import validate_phone_number, validate_alphanumeric_spaces


class CustomerModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='customer_profile',
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        max_length=100,
        validators=[validate_alphanumeric_spaces]
    )
    last_name = models.CharField(
        max_length=100,
        validators=[validate_alphanumeric_spaces]
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message='Email invalide')]
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone_number]
    )
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower().strip()

    def __str__(self):
        return f"{self.email} ({self.first_name} {self.last_name})"
