from django.urls import path, include

urlpatterns = [
    path('customers/', include('app.customers.urls')),
    path('rooms/', include('app.rooms.urls')),
    path('activity/', include('app.activity.urls')),
    path('reservation/', include('app.reservation.urls')),
    path('reservationActivity/', include('app.reservationActivity.urls')),
    path('reviews/', include('app.reviews.urls')),
]