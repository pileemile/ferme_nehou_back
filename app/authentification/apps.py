from django.apps import AppConfig


class AuthentificationConfig(AppConfig):
    name = 'app.authentification'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import app.authentification.signals  # noqa: F401
