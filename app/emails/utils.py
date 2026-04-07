import qrcode
import io
import base64
from PIL import Image


def generate_qr_code(data):
    """
    Génère un QR code et le retourne en base64

    Args:
        data (str): Données à encoder dans le QR code

    Returns:
        str: Image QR code en base64
    """
    # Créer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Générer l'image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convertir en base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def generate_reservation_qr_code(reservation):
    """
    Génère un QR code pour une réservation

    Format des données :
    RESERVATION:ID:CLIENT:ROOM:DATES
    """
    data = (
        f"RESERVATION\n"
        f"ID: {reservation.id}\n"
        f"Client: {reservation.client.first_name} {reservation.client.last_name}\n"
        f"Chambre: {reservation.room.name}\n"
        f"Arrivée: {reservation.check_in_date.strftime('%d/%m/%Y')}\n"
        f"Départ: {reservation.check_out_date.strftime('%d/%m/%Y')}\n"
        f"Voyageurs: {reservation.guest_count}"
    )

    return generate_qr_code(data)