from rest_framework import serializers

from app.activity.models import Activity
from app.photo.serializers import SerializerPhoto


class SerializerActivity(serializers.ModelSerializer):
    photo_url = SerializerPhoto(many=True, read_only=True)
    class Meta:
        model = Activity
        fields = [
            'id',
            'name',
            'description',
            'price',
            'available',
            'photo',
            'photo_url',
            'icon'
        ]