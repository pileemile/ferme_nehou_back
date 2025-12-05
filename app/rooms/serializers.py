from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from app.rooms.models import RoomModel, AmenityModel


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
            'amenities'
    ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_main_photo(self, obj):
        if obj.main_photo:
            return self.context['request'].build_absolute_uri(obj.main_photo.url)
        return None