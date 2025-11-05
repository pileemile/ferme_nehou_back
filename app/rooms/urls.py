from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.rooms.views import RoomViewSet

router = SimpleRouter()

router.register("", RoomViewSet, basename="rooms")

urlpatterns = [
    path("", include(router.urls)),
]