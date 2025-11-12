from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.reservation.views import ReservationViewSet

router = SimpleRouter()

router.register('', ReservationViewSet, basename='reservations')

urlpatterns = [
    path('', include(router.urls)),
]