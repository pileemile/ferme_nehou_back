from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from app.authentification.views import (
    AdminRegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/admin/', AdminRegisterView.as_view(), name='register_admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
