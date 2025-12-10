from datetime import datetime

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.reservation.models import Reservation
from app.rooms.filter import RoomFilter
from app.rooms.models import RoomModel
from app.rooms.serializers import SerializerRooms


class RoomViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = SerializerRooms
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter

    def get_queryset(self):
        return RoomModel.objects.all().prefetch_related('amenities', 'photos')

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        room = self.get_object()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {'error' : 'Les paramètres start_date et end_date sont obligatoires'},
                status= status.HTTP_400_BAD_REQUEST
            )
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error' : 'Format de la date incorrect'},
                status= status.HTTP_400_BAD_REQUEST
            )

        conflicting = Reservation.objects.filter(
            room = room,
            status__in=['pending', 'confirmed'],
            check_in_date__lte=end_date,
            check_out_date__gte=start_date
        )
        available = not conflicting.exists()

        conflicting_data =  []
        if not available:
            for res in conflicting:
                conflicting_data.append({
                    'id' : res.id,
                    'check_in_date' : res.check_in_date,
                    'check_out_date' : res.check_out_date,
                    'status' : res.status
                })
        return Response({
            'room_id' : room.id,
            'room_name' : room.name,
            'start_date' : start_date,
            'end_date' : end_date,
            'available' : available,
            'conflicting_reservations' : conflicting_data
            })
    @action(detail=False, methods=['get'])
    def search(self, request):
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        guests = request.query_params.get('guests')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        queryset = self.get_queryset()

        if guests:
            queryset = queryset.filter(capacity__gte=int(guests))

        if min_price:
            queryset = queryset.filter(price_per_night__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price_per_night__lte=float(max_price))

        if check_in and check_out:
            try:
                check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out, '%Y-%m-%d').date()

                unavailable_rooms = Reservation.objects.filter(
                    status__in=['pending', 'confirmed'],
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                ).values_list('room_id', flat=True)

                queryset = queryset.exclude(id__in=unavailable_rooms)
            except ValueError:
                return Response(
                    {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count' : queryset.count(),
            'results' : serializer.data
        })

    @action(detail=True, methods=['get'])
    def calendar(self, request, pk=None):
        room = self.get_object()

        reservations = Reservation.objects.filter(
            room=room,
            status__in=['pending', 'confirmed'],
            check_out_date__gte=timezone.now().date()
        ).order_by('check_in_date')

        calendar_data = []
        for res in reservations:
            calendar_data.append({
                'id': res.id,
                'check_in': res.check_in_date,
                'check_out': res.check_out_date,
                'status': res.status,
                'guest_count': res.guest_count
            })

        return Response({
            'room_id': room.id,
            'room_name': room.name,
            'reservations': calendar_data
        })