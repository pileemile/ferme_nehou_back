from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


class EmailService:
    """Service pour envoyer des emails"""

    @staticmethod
    def send_reservation_confirmation(reservation):
        """Envoyer email de confirmation de réservation"""
        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'reservation_id': reservation.id,
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date.strftime('%d/%m/%Y'),
            'check_out_date': reservation.check_out_date.strftime('%d/%m/%Y'),
            'number_of_nights': reservation.get_number_of_nights(),
            'guest_count': reservation.guest_count,
            'total_price': reservation.total_price,
            'activities': reservation.reservationactivity_set.all()
        }

        html_content = render_to_string('reservation_confirmation.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f'Confirmation de réservation #{reservation.id} - Ferme de Néhou',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_reservation_reminder(reservation):
        """Envoyer rappel 3 jours avant l'arrivée"""
        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'reservation_id': reservation.id,
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date.strftime('%d/%m/%Y'),
            'check_out_date': reservation.check_out_date.strftime('%d/%m/%Y'),
        }

        html_content = render_to_string('reservation_reminder.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f'Rappel : Votre séjour arrive bientôt !',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_reservation_cancelled(reservation, refund_info):
        """Envoyer email d'annulation"""
        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'reservation_id': reservation.id,
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date.strftime('%d/%m/%Y'),
            'check_out_date': reservation.check_out_date.strftime('%d/%m/%Y'),
            'refund_info': refund_info
        }

        html_content = render_to_string('reservation_cancelled.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f'Annulation de réservation #{reservation.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_review_request(reservation):
        """Envoyer demande d'avis après le séjour"""
        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'reservation_id': reservation.id,
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date.strftime('%d/%m/%Y'),
            'check_out_date': reservation.check_out_date.strftime('%d/%m/%Y'),
        }

        html_content = render_to_string('review_request.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject='Comment s\'est passé votre séjour ?',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_admin_new_reservation(reservation):
        """Notifier l'admin d'une nouvelle réservation"""
        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'customer_email': reservation.client.email,
            'customer_phone': reservation.client.phone,
            'reservation_id': reservation.id,
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date.strftime('%d/%m/%Y'),
            'check_out_date': reservation.check_out_date.strftime('%d/%m/%Y'),
            'guest_count': reservation.guest_count,
            'total_price': reservation.total_price,
        }

        html_content = render_to_string('admin_new_reservation.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f'Nouvelle réservation #{reservation.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()