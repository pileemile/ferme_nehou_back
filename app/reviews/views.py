from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

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
    serializer_class = SerializerReviews
    def get_queryset(self):
        return Review.objects.all()