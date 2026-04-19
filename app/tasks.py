from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from app.emails.service import EmailService
from app.reservation.models import Reservation
from app.notifications.services import NotificationService


@shared_task
def send_reservation_confirmation_async(reservation_id):
    """Envoyer email de confirmation en arrière-plan"""
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        EmailService.send_reservation_confirmation(reservation)
        return f"Email de confirmation envoyé pour réservation #{reservation_id}"
    except Reservation.DoesNotExist:
        return f"Réservation #{reservation_id} introuvable"


@shared_task
def send_admin_notification_async(reservation_id):
    """Notifier l'admin en arrière-plan"""
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        EmailService.send_admin_new_reservation(reservation)
        return f"Email admin envoyé pour réservation #{reservation_id}"
    except Reservation.DoesNotExist:
        return f"Réservation #{reservation_id} introuvable"


@shared_task
def send_reminder_emails():
    """
    Envoyer emails ET notifications de rappel 3 jours avant l'arrivée
    À exécuter quotidiennement à 9h
    """
    target_date = timezone.now().date() + timedelta(days=3)

    reservations = Reservation.objects.filter(
        check_in_date=target_date,
        status='confirmed'
    )

    count = 0
    for reservation in reservations:
        # Envoyer email
        EmailService.send_reservation_reminder(reservation)

        # Créer notification in-app
        NotificationService.notify_reservation_reminder(reservation)

        count += 1

    return f"{count} emails/notifications de rappel envoyés"


@shared_task
def send_thank_you_emails():
    """
    Envoyer emails de remerciement le jour du départ
    À exécuter quotidiennement à 10h
    """
    today = timezone.now().date()

    reservations = Reservation.objects.filter(
        check_out_date=today,
        status='confirmed'
    )

    count = 0
    for reservation in reservations:
        # Envoyer email
        EmailService.send_thank_you_email(reservation)

        # Marquer comme terminée
        reservation.status = 'completed'
        reservation.save()

        count += 1

    return f"{count} emails de remerciement envoyés"


@shared_task
def send_review_request_emails():
    """
    Envoyer demande d'avis 2 jours après le départ
    À exécuter quotidiennement à 14h
    """
    target_date = timezone.now().date() - timedelta(days=2)

    reservations = Reservation.objects.filter(
        check_out_date=target_date,
        status='completed'
    )

    count = 0
    for reservation in reservations:
        # Vérifier qu'il n'a pas déjà laissé d'avis
        if not hasattr(reservation, 'review'):
            # Envoyer email
            EmailService.send_review_request(reservation)

            # Créer notification
            NotificationService.notify_review_request(reservation)

            count += 1

    return f"{count} demandes d'avis envoyées"


@shared_task
def cleanup_old_notifications():
    """
    Supprimer les notifications lues de plus de 30 jours
    À exécuter chaque lundi à 3h
    """
    from app.notifications.models import Notification

    cutoff_date = timezone.now() - timedelta(days=30)

    count = Notification.objects.filter(
        is_read=True,
        read_at__lt=cutoff_date
    ).delete()[0]

    return f"{count} anciennes notifications supprimées"


@shared_task(bind=True)
def debug_task(self):
    """Tâche de debug"""
    print(f'Request: {self.request!r}')
    return 'Debug task executed'