from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import StatsViewSet

router = SimpleRouter()
router.register('', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]