from rest_framework import serializers

from app.customers.serializers import SerializerCustomers
from app.reservation.models import Reservation
from app.reservationActivity.serializers import SerializerReservationActivity
from app.rooms.serializers import SerializerRooms


class ReservationSerializer(serializers.ModelSerializer):
    client_details = SerializerCustomers(source='client', read_only=True)
    room_details = SerializerRooms(source='room' , read_only=True)
    activities = SerializerReservationActivity(many=True, read_only=True)
    number_of_nights = serializers.IntegerField(source='get_number_of_nights', read_only=True)
    class Meta:
        model = Reservation
        fields = [
            'id',
            'client',
            'client_details',
            'room',
            'room_details',
            'check_in_date',
            'check_out_date',
            'guest_count',
            'status',
            'total_price',
            'number_of_nights',
            'activities',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['total_price','created_at', 'updated_at']

    def validate(self, data):
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')

        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({
                'check_out_date' : 'La date de départ doit être après la date d\'arrivée.'
            })
        return data