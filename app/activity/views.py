from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime

from app.activity.models import Activity
from app.activity.serializers import SerializerActivity
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
    def get_queryset(self):
        return Activity.objects.all()

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Endpoint: GET /api/activity/available/?date=YYYY-MM-DD

        Retourne les activités disponibles pour une date donnée
        """
        date_param = request.query_params.get('date')

        # Si pas de date, retourner toutes les activités disponibles
        if not date_param:
            activities = self.get_queryset().filter(available=True)
            serializer = self.get_serializer(activities, many=True)
            return Response({
                'date': 'any',
                'count': activities.count(),
                'activities': serializer.data
            })

        # Valider le format de date
        try:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {
                    'error': 'Format de date invalide. Utilisez YYYY-MM-DD',
                    'example': '2025-12-10'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Pour l'instant, on retourne simplement les activités disponibles
        # Plus tard, on pourra ajouter une logique de capacité/réservation
        activities = self.get_queryset().filter(available=True)

        serializer = self.get_serializer(activities, many=True)

        return Response({
            'date': date_param,
            'count': activities.count(),
            'activities': serializer.data,
            'note': 'Toutes les activités sont disponibles à cette date. La gestion des capacités sera ajoutée plus tard.'
        })

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