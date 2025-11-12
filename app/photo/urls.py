from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.photo.views import PhotoViewSet

router = SimpleRouter()

router.register('', PhotoViewSet, basename='photos')

urlpatterns = [
    path('', include(router.urls)),
]