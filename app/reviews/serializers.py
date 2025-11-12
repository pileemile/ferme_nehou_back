from rest_framework import serializers

from app.reviews.models import Review


class SerializerReviews(serializers.ModelSerializer):
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