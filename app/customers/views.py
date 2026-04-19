from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.emails.service import EmailService
from app.permissions import IsAdminUser
from app.customers.models import CustomerModel
from app.customers.serializers import SerializerCustomers
from app.utils.customers import ensure_customer_for_user


class CustomerViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = SerializerCustomers

    def get_permissions(self):
        if self.action in {"destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = CustomerModel.objects.select_related("user")
        if self.request.user.is_staff:
            return queryset

        customer = ensure_customer_for_user(self.request.user)
        if customer is None:
            return CustomerModel.objects.none()
        return queryset.filter(pk=customer.pk)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        customer = ensure_customer_for_user(request.user)
        if customer is None:
            return Response(
                {"error": "Aucun profil client n'est associé à cet utilisateur."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "GET":
            serializer = self.get_serializer(customer)
            return Response(serializer.data)

        serializer = self.get_serializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def send_welcome(self, request):
        customer = ensure_customer_for_user(request.user)
        if customer is None:
            return Response(
                {"error": "Aucun profil client n'est associé à cet utilisateur."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        EmailService.send_welcome_email(customer)
        return Response({"message": "Email de bienvenue envoyé."})
