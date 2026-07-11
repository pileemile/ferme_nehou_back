from django.conf import settings
from django.core.cache import cache
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.cache import invalidate_review_cache, make_cache_key
from app.pagination import CustomPageNumberPagination
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
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Review.objects.all().select_related(
            'client',
            'room',
            'reservation',
        ).order_by('-created_at')

    def perform_create(self, serializer):
        customer = get_customer_for_user(self.request.user)
        if customer is None:
            raise ValidationError(
                {"client": "Aucun profil client n'est associé à cet utilisateur."}
            )
        instance = serializer.save(client=customer)
        invalidate_review_cache(room_id=instance.room_id)

    def perform_update(self, serializer):
        review = self.get_object()
        instance = serializer.save(client=review.client)
        invalidate_review_cache(room_id=instance.room_id)

    def perform_destroy(self, instance):
        room_id = instance.room_id
        instance.delete()
        invalidate_review_cache(room_id=room_id)

    @action(detail=False, methods=['get'])
    def recent(self, request):
      """
      GET /api/reviews/recent/?limit=10&room_id=1

      Retourne les derniers avis
      Paramètres :
      - limit : nombre d'avis (défaut: 10, max: 50)
      - room_id : filtrer par chambre (optionnel)
      """
      try:
        limit = int(request.query_params.get('limit', 10))
      except (TypeError, ValueError):
        limit = 10
      room_id = request.query_params.get('room_id')

      if limit > 50:
        limit = 50
      if limit < 1:
        limit = 1

      cache_key = make_cache_key('reviews_recent', {'limit': limit, 'room_id': room_id})
      cached_data = cache.get(cache_key)

      if cached_data is not None:
        return Response(cached_data)

      queryset = self.get_queryset()

      # Filtrer par chambre si spécifié
      if room_id:
        queryset = queryset.filter(room_id=room_id)

      reviews = queryset[:limit]
      serializer = self.get_serializer(reviews, many=True, context={'request': request})

      data = {
        'limit': limit,
        'room_id': room_id,
        'count': len(serializer.data),
        'reviews': serializer.data
      }

      cache.set(cache_key, data, settings.CACHE_TTL_REVIEWS)

      return Response(data)
