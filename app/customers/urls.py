from django.urls import path, include
from rest_framework.routers import SimpleRouter

from app.customers.views import CustomerViewSet

router = SimpleRouter()

router.register('', CustomerViewSet, basename='customers')

urlpatterns = [
    path('', include(router.urls)),
]