from rest_framework import serializers

from app.customers.serializers import SerializerCustomers
from app.reviews.models import Review


class SerializerReviews(serializers.ModelSerializer):
    client = SerializerCustomers(read_only=True)
    class Meta:
        model = Review
        fields = [
            'id',
            'client',
            'room',
            'rating',
            'comment',
            'created_at',
        ]