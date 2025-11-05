from django.urls import path, include

urlpatterns = [
    path('customers/', include('app.customers.urls')),
    path('rooms/', include('app.rooms.urls')),
]