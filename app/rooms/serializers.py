import bleach
from django.db.models import Avg
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from app.photo.serializers import SerializerPhoto
from app.reviews.models import Review
from app.rooms.models import RoomModel, AmenityModel
from app.validators import validate_price


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AmenityModel
        fields = [
            'id',
            'name',
            'icon'
        ]


class SerializerRooms(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)
    photos = SerializerPhoto(many=True, read_only=True)

    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    class Meta:
        model = RoomModel
        fields = [
            'id',
            'name',
            'description',
            'capacity',
            'price_per_night',
            'available',
            'main_photo',
            'amenities',
            'photos',
            'average_rating',
            'total_reviews',
    ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_main_photo(self, obj):
        if obj.main_photo:
            return self.context['request'].build_absolute_uri(obj.main_photo.url)
        return None

    def get_average_rating(self, obj):
        avg = Review.objects.filter(room=obj).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 2) if avg else None
    def get_total_reviews(self, obj):
        return Review.objects.filter(room=obj).count()

    def validate_price_per_night(self, value):
        validate_price(value)
        if value > 10000:
            raise serializers.ValidationError('Le prix ne peut pas dépasser 10000€')
        return value

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError('La capacité doit être supérieure à 0')
        if value > 50:
            raise serializers.ValidationError('La capacité ne peut pas dépasser 50 personnes')
        return value

    def validate_name(self, value):
        return bleach.clean(value.strip())

    def validate_description(self, value):
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
        return bleach.clean(value.strip(), tags=allowed_tags)