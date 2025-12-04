from rest_framework import serializers

from app.rooms.amenityModel import AmenityModel


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AmenityModel
        fields = [
            'id',
            'name',
            'icon'
        ]
