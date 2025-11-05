from rest_framework import serializers

from app.rooms.models import RoomModel


class SerializerRooms(serializers.ModelSerializer):
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
        ]