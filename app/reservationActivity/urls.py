from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.reservationActivity.views import ReservationActivityViewSet

router = SimpleRouter()

router.register("", ReservationActivityViewSet, basename="reservation_activities")

urlpatterns = [
    path("", include(router.urls)),
]