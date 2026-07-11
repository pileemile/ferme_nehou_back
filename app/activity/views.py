from django.conf import settings
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from app.cache import make_cache_key
from app.activity.models import Activity
from app.activity.serializers import SerializerActivity
from app.activity.filters import ActivityFilter
from app.pagination import CustomPageNumberPagination
from app.permissions import IsAdminUser


class ActivityViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = [IsAdminUser]
    serializer_class = SerializerActivity
    filter_backends = [DjangoFilterBackend]
    filterset_class = ActivityFilter
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Activity.objects.all()

    def list(self, request, *args, **kwargs):
        """Liste des activités avec cache"""
        cache_key = make_cache_key('activities_list', dict(request.query_params))
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        if response.status_code == 200:
            cache.set(cache_key, response.data, settings.CACHE_TTL_ACTIVITIES)

        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.delete_pattern('activities_*')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.delete_pattern('activities_*')

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.delete_pattern('activities_*')

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Endpoint: GET /api/activity/available/?date=YYYY-MM-DD

        Retourne les activités disponibles pour une date donnée
        """
        date_param = request.query_params.get('date')
        cache_key = make_cache_key('activities_available', {'date': date_param})
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        activities = self.get_queryset().filter(available=True)

        if date_param:
            try:
                datetime.strptime(date_param, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(activities, many=True)
        data = {
            'date': date_param or 'any',
            'count': activities.count(),
            'activities': serializer.data
        }

        cache.set(cache_key, data, settings.CACHE_TTL_ACTIVITIES)

        return Response(data)

    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        """
        Endpoint: GET /api/activity/{id}/check_availability/?date=YYYY-MM-DD&quantity=2

        Vérifier si une activité est disponible pour une date et quantité
        """
        activity = self.get_object()
        date_param = request.query_params.get('date')
        quantity = request.query_params.get('quantity', 1)

        if not date_param:
            return Response(
                {'error': 'Le paramètre date est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Format invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Pour l'instant, simplement vérifier si disponible
        available = activity.available

        return Response({
            'activity_id': activity.id,
            'activity_name': activity.name,
            'date': date_param,
            'quantity_requested': quantity,
            'available': available,
            'price_per_unit': float(activity.price),
            'total_price': float(activity.price) * quantity if available else None
        })
