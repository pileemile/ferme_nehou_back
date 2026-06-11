from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.permissions import CanReviewReservation
from app.reviews.models import Review
from app.reviews.serializers import SerializerReviews
from app.utils.customers import get_customer_for_user


class ReviewViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = [CanReviewReservation]
    serializer_class = SerializerReviews

    def get_queryset(self):
        return Review.objects.all().select_related('client', 'room', 'reservation')

    def perform_create(self, serializer):
        customer = get_customer_for_user(self.request.user)
        if customer is None:
            raise ValidationError(
                {"client": "Aucun profil client n'est associé à cet utilisateur."}
            )
        serializer.save(client=customer)

    def perform_update(self, serializer):
        review = self.get_object()
        serializer.save(client=review.client)

    @action(detail=False, methods=['get'])
    def recent(self, request):
      """
      GET /api/reviews/recent/?limit=10&room_id=1

      Retourne les derniers avis
      Paramètres :
      - limit : nombre d'avis (défaut: 10, max: 50)
      - room_id : filtrer par chambre (optionnel)
      """
      limit = int(request.query_params.get('limit', 10))
      room_id = request.query_params.get('room_id')

      if limit > 50:
        limit = 50

      queryset = self.get_queryset().order_by('-created_at')

      # Filtrer par chambre si spécifié
      if room_id:
        queryset = queryset.filter(room_id=room_id)

      reviews = queryset[:limit]
      serializer = self.get_serializer(reviews, many=True, context={'request': request})

      return Response({
        'limit': limit,
        'room_id': room_id,
        'count': len(serializer.data),
        'reviews': serializer.data
      })
