from .models import Notification


class NotificationService:
    """Service pour créer des notifications"""

    @staticmethod
    def create_notification(user, title, message, notification_type='info', link=None, metadata=None):
        """Créer une notification"""
        return Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            link=link,
            metadata=metadata or {}
        )

    @staticmethod
    def notify_reservation_confirmed(reservation):
        """Notifier que la réservation est confirmée"""
        return NotificationService.create_notification(
            user=reservation.client,
            title="Réservation confirmée",
            message=f"Votre réservation #{reservation.id} pour {reservation.room.name} a été confirmée !",
            notification_type='reservation',
            link=f"/reservations/{reservation.id}",
            metadata={
                'reservation_id': reservation.id,
                'room_name': reservation.room.name,
                'check_in': str(reservation.check_in_date),
                'check_out': str(reservation.check_out_date)
            }
        )

    @staticmethod
    def notify_reservation_reminder(reservation):
        """Rappel avant l'arrivée"""
        days = (reservation.check_in_date - timezone.now().date()).days
        return NotificationService.create_notification(
            user=reservation.client,
            title=f"Votre séjour arrive dans {days} jours !",
            message=f"N'oubliez pas votre réservation à {reservation.room.name} le {reservation.check_in_date.strftime('%d/%m/%Y')}.",
            notification_type='info',
            link=f"/reservations/{reservation.id}"
        )

    @staticmethod
    def notify_reservation_cancelled(reservation):
        """Notifier l'annulation"""
        return NotificationService.create_notification(
            user=reservation.client,
            title="Réservation annulée",
            message=f"Votre réservation #{reservation.id} a été annulée.",
            notification_type='warning',
            link=f"/reservations/{reservation.id}"
        )

    @staticmethod
    def notify_review_request(reservation):
        """Demander un avis"""
        return NotificationService.create_notification(
            user=reservation.client,
            title="Laissez un avis sur votre séjour",
            message=f"Partagez votre expérience à {reservation.room.name} !",
            notification_type='review',
            link=f"/reviews/new?reservation={reservation.id}"
        )

    @staticmethod
    def notify_payment_success(reservation):
        """Paiement réussi"""
        return NotificationService.create_notification(
            user=reservation.client,
            title="Paiement confirmé",
            message=f"Votre paiement de {reservation.total_price}€ a été reçu.",
            notification_type='payment',
            link=f"/reservations/{reservation.id}"
        )