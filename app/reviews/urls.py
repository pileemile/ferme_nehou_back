from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.reviews.views import ReviewViewSet

router = SimpleRouter()

router.register('', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
]

