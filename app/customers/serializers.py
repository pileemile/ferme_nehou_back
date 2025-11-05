from rest_framework import serializers

from app.customers.models import CustomerModel


class SerializerCustomers(serializers.ModelSerializer):
    class Meta:
        model = CustomerModel
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'created_at',
        ]