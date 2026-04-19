from rest_framework import serializers

from app.customers.serializers import SerializerCustomers
from app.reservation.models import Reservation
from app.reviews.models import Review
from app.utils.customers import get_customer_for_user


class SerializerReviews(serializers.ModelSerializer):
    client_detail = SerializerCustomers(read_only=True)
    client_name = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = [
            'id',
            'client',
            'client_detail',
            'client_name',
            'room',
            'reservation',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['client', 'created_at']

    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("la doit être comprise entre 1 et 5")
        return value
    def validate(self, data):
        client = data.get('client')
        if client is None:
            if self.instance is not None:
                client = self.instance.client
            else:
                request = self.context.get('request')
                if request is not None:
                    client = get_customer_for_user(request.user)
        room = data.get('room')
        reservation = data.get('reservation')

        if client and room:
            has_valid_reservation = Reservation.objects.filter(
                client = client,
                room = room,
                status__in=['confirmed', 'completed']
            ).exists()
            if not has_valid_reservation:
                raise serializers.ValidationError({
                    'client' : "Vous devez avoir effectué une réservation confirmé pour laisser un avis"
                })
        if reservation:
            if reservation.client != client:
                raise serializers.ValidationError({
                    'reservation' : "cette réservation n\'appartient pas à ce client"
                })
            if reservation.room != room:
                raise serializers.ValidationError({
                    'reservation' : "cette réservation ne concerne pas cette chambre"
                })
            existing = Review.objects.filter(reservation = reservation)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError({
                    'reservation' : "Un avis existe déjà pour cette réservation"
                })
        return data
    class RoomAverageRatingSerializer(serializers.Serializer):
        room_id = serializers.IntegerField()
        room_name = serializers.CharField()
        average_rating = serializers.FloatField()
        total_reviews = serializers.IntegerField()
