from django.apps import AppConfig


class ReservationConfig(AppConfig):
    name = 'app.reservation'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import app.reservation.signals