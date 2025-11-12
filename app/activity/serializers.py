from rest_framework import serializers

from app.activity.models import Activity


class SerializerActivity(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            'id',
            'name',
            'description',
            'price',
            'available',
        ]