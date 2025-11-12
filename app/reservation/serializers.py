from rest_framework import serializers

from app.reservation.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id',
            'client',
            'room',
            'check_in_date',
            'check_out_date',
            'guest_count',
            'status',
            'total_price'
        ]