from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from app.emails.service import EmailService
from app.reservation.models import Reservation


@shared_task
def send_reminder_emails():
    """
    Envoyer emails de rappel 3 jours avant l'arrivée
    À exécuter quotidiennement
    """
    target_date = timezone.now().date() + timedelta(days=3)

    reservations = Reservation.objects.filter(
        check_in_date=target_date,
        status='confirmed'
    )

    for reservation in reservations:
        EmailService.send_reservation_reminder(reservation)


@shared_task
def send_thank_you_emails():
    """
    Envoyer emails de remerciement le jour du départ
    À exécuter quotidiennement
    """
    today = timezone.now().date()

    reservations = Reservation.objects.filter(
        check_out_date=today,
        status='confirmed'
    )

    for reservation in reservations:
        EmailService.send_thank_you_email(reservation)
        # Marquer comme terminée
        reservation.status = 'completed'
        reservation.save()


@shared_task
def send_review_request_emails():
    """
    Envoyer demande d'avis 2 jours après le départ
    À exécuter quotidiennement
    """
    target_date = timezone.now().date() - timedelta(days=2)

    reservations = Reservation.objects.filter(
        check_out_date=target_date,
        status='completed'
    )

    for reservation in reservations:
        # Vérifier qu'il n'a pas déjà laissé d'avis
        if not hasattr(reservation, 'review'):
            EmailService.send_review_request(reservation)