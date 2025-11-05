from django.urls import path, include

urlpatterns = [
    path('customers/', include('app.customers.urls')),
]