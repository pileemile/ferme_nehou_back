from rest_framework import serializers

from app.reservationActivity.models import ReservationActivity


class SerializerReservationActivity(serializers.ModelSerializer):
    class Meta:
        model = ReservationActivity
        fields = [
            'id',
            'reservation',
            'activity',
            'quantity',
        ]