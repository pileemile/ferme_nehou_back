import bleach
from rest_framework import serializers
from django.core.validators import EmailValidator
from app.customers.models import CustomerModel
from app.validators import validate_phone_number


class SerializerCustomers(serializers.ModelSerializer):
    class Meta:
        model = CustomerModel
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate_email(self, value):
        """Validation et nettoyage de l'email"""
        # Convertir en minuscules et supprimer espaces
        value = value.lower().strip()

        # Vérifier le format
        validator = EmailValidator()
        validator(value)

        return value

    def validate_phone(self, value):
        if value:
            value = value.strip()
            validate_phone_number(value)
        return value

    def validate_first_name(self, value):
        return bleach.clean(value.strip())

    def validate_last_name(self, value):
        return bleach.clean(value.strip())

    def validate_address(self, value):
        allowed_tags = []
        return bleach.clean(value.strip(), tags=allowed_tags)
