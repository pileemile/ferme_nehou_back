from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.rooms.amenityViews import AmenityViewSet
from app.rooms.views import RoomViewSet

router = SimpleRouter()

router.register("rooms", RoomViewSet, basename="rooms")
router.register("amenities", AmenityViewSet, basename="amenities")

urlpatterns = [
    path("", include(router.urls)),
]