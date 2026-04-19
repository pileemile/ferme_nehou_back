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
        limit = request.query_params.get('limit', 10)
        reviews = self.get_queryset()[:int(limit)]
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
