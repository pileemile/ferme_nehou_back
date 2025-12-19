from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.permissions import CanReviewReservation
from app.reviews.models import Review
from app.reviews.serializers import SerializerReviews


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

    @action(detail=False, methods=['get'])
    def recent(self, request):
        limit = request.query_params.get('limit', 10)
        reviews = self.get_queryset()[:int(limit)]
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
