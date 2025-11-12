from rest_framework import serializers
from .models import Photo


class SerializerPhoto(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            'id',
            'room',
            'file_url',
            'description',
        ]
