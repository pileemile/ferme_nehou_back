from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from .utils import generate_reservation_qr_code


class EmailService:
    """Service centralisé pour l'envoi d'emails"""

    @staticmethod
    def send_welcome_email(customer):
        """Email de bienvenue à l'inscription"""
        context = {
            'customer_name': f"{customer.first_name} {customer.last_name}",
        }

        html_content = render_to_string('welcome.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject='Bienvenue à la Ferme de Néhou 🏡',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_reservation_confirmation(reservation):
        """Email de confirmation avec QR code"""
        # Générer le QR code
        qr_code = generate_reservation_qr_code(reservation)

        # Récupérer les activités
        activities = []
        for res_activity in reservation.activities.all():
            activities.append({
                'name': res_activity.activity.name,
                'quantity': res_activity.quantity,
                'price': res_activity.activity.price
            })

        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'reservation_id': reservation.id,
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date.strftime('%d/%m/%Y'),
            'check_out_date': reservation.check_out_date.strftime('%d/%m/%Y'),
            'number_of_nights': reservation.get_number_of_nights(),
            'guest_count': reservation.guest_count,
            'total_price': reservation.total_price,
            'activities': activities,
            'qr_code': qr_code
        }

        html_content = render_to_string('reservation_confirmation.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f'✅ Confirmation de réservation #{reservation.id} - Ferme de Néhou',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_reservation_reminder(reservation):
        """Email de rappel 3 jours avant l'arrivée"""
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
            subject=f'🗓️ Rappel : Votre séjour arrive dans 3 jours !',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_reservation_modified(reservation, changes):
        """Email de modification de réservation"""
        # Générer le nouveau QR code
        qr_code = generate_reservation_qr_code(reservation)

        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'reservation_id': reservation.id,
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date.strftime('%d/%m/%Y'),
            'check_out_date': reservation.check_out_date.strftime('%d/%m/%Y'),
            'guest_count': reservation.guest_count,
            'total_price': reservation.total_price,
            'changes': changes,
            'qr_code': qr_code
        }

        html_content = render_to_string('reservation_modified.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f'✏️ Modification de réservation #{reservation.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_reservation_cancelled(reservation, refund_info):
        """Email d'annulation"""
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
            subject=f'❌ Annulation de réservation #{reservation.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_thank_you_email(reservation):
        """Email de remerciement après le séjour"""
        # Date d'expiration de l'offre : 3 mois après le départ
        offer_expiry = (reservation.check_out_date + timedelta(days=90)).strftime('%d/%m/%Y')

        context = {
            'customer_name': f"{reservation.client.first_name} {reservation.client.last_name}",
            'room_name': reservation.room.name,
            'offer_expiry': offer_expiry
        }

        html_content = render_to_string('thank_you.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject='🙏 Merci pour votre séjour à la Ferme de Néhou',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_review_request(reservation):
        """Email de demande d'avis 2 jours après le départ"""
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
            subject='⭐ Partagez votre expérience à la Ferme de Néhou',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.client.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_admin_new_reservation(reservation):
        """Notification admin - nouvelle réservation"""
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
            subject=f'🔔 Nouvelle réservation #{reservation.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
