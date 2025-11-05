from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.activity.views import ActivityViewSet

router = SimpleRouter()

router.register("", ActivityViewSet, basename="activities")

urlpatterns = [
    path("", include(router.urls)),
]