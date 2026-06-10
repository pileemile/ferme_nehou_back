import os
from celery import Celery
from celery.schedules import crontab

# Définir le settings par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet_ferme_nehou_back.settings')

app = Celery('projet_ferme_nehou_back')

# Charger la config depuis settings.py avec le préfixe CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans tous les fichiers tasks.py
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    # Envoyer emails de rappel tous les jours à 9h
    'send-reminder-emails-daily': {
        'task': 'app.tasks.send_reminder_emails',
        'schedule': crontab(hour=9, minute=0),
    },
    # Envoyer emails de remerciement tous les jours à 10h
    'send-thank-you-emails-daily': {
        'task': 'app.tasks.send_thank_you_emails',
        'schedule': crontab(hour=10, minute=0),
    },
    # Envoyer demandes d'avis tous les jours à 14h
    'send-review-request-emails-daily': {
        'task': 'app.tasks.send_review_request_emails',
        'schedule': crontab(hour=14, minute=0),
    },
    # Nettoyer les anciennes notifications tous les lundis à 3h
    'cleanup-old-notifications-weekly': {
        'task': 'app.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')