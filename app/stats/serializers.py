from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Statistiques générales du dashboard"""
    total_reservations = serializers.IntegerField()
    active_reservations = serializers.IntegerField()
    pending_reservations = serializers.IntegerField()
    completed_reservations = serializers.IntegerField()
    cancelled_reservations = serializers.IntegerField()

    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_month_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

    total_customers = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()

    occupancy_rate = serializers.FloatField()


class ReservationStatsSerializer(serializers.Serializer):
    """Statistiques des réservations"""
    period = serializers.CharField()
    reservations_count = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_booking_value = serializers.DecimalField(max_digits=10, decimal_places=2)


class OccupancyStatsSerializer(serializers.Serializer):
    """Statistiques d'occupation"""
    room_id = serializers.IntegerField()
    room_name = serializers.CharField()
    total_days = serializers.IntegerField()
    booked_days = serializers.IntegerField()
    available_days = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()


class PopularRoomSerializer(serializers.Serializer):
    """Chambres populaires"""
    room_id = serializers.IntegerField()
    room_name = serializers.CharField()
    reservations_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()


class RevenueStatsSerializer(serializers.Serializer):
    """Statistiques de chiffre d'affaires"""
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    reservations_count = serializers.IntegerField()
    average_booking_value = serializers.DecimalField(max_digits=10, decimal_places=2)