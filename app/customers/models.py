from django.db import models
from django.core.validators import EmailValidator
from app.validators import validate_phone_number, validate_alphanumeric_spaces


class CustomerModel(models.Model):
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