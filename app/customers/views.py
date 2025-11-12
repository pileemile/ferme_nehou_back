from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from app.customers.models import CustomerModel
from app.customers.serializers import SerializerCustomers


class CustomerViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class =SerializerCustomers
    def get_queryset(self):
        return CustomerModel.objects.all()