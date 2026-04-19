from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer
from app.utils.customers import get_customer_for_user


class NotificationViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_customer_for_user(self.request.user)
        if customer is None:
            return Notification.objects.none()
        return Notification.objects.filter(user=customer)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Obtenir uniquement les notifications non lues"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Compter les notifications non lues"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marquer toutes les notifications comme lues"""
        notifications = self.get_queryset().filter(is_read=False)
        count = notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'marked_as_read': count})

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Supprimer toutes les notifications lues"""
        count = self.get_queryset().filter(is_read=True).delete()[0]
        return Response({'deleted': count})
