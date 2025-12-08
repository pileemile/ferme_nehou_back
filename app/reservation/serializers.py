from rest_framework import serializers

from app.customers.serializers import SerializerCustomers
from app.reservation.models import Reservation
from app.reservationActivity.serializers import SerializerReservationActivity
from app.rooms.serializers import SerializerRooms


class ReservationSerializer(serializers.ModelSerializer):
    client = SerializerCustomers(read_only=True)
    room = SerializerRooms(read_only=True)
    activities = SerializerReservationActivity(many=True, read_only=True)
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
            'total_price',
            'activities'
        ]