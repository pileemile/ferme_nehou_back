from app.emails.service import EmailService
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

    def create(self, request, *args, **kwargs):
        """Créer un client et envoyer email de bienvenue"""
        response = super().create(request, *args, **kwargs)
        customer = CustomerModel.objects.get(pk=response.data['id'])

        # Envoyer email de bienvenue
        EmailService.send_welcome_email(customer)

        return response