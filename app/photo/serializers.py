from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Photo

class SerializerPhoto(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            'id',
            'room',
            'file',
            'file_url',
            'description',
        ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
