from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from app.customers.models import CustomerModel
from app.reservation.models import Reservation
from app.rooms.models import AmenityModel, RoomModel


class RoomEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.today = timezone.now().date()
        self.check_in = self.today + timedelta(days=10)
        self.check_out = self.today + timedelta(days=13)

        self.wifi = AmenityModel.objects.create(name="WiFi", icon="wifi")
        self.spa = AmenityModel.objects.create(name="Spa", icon="spa")

        self.room_free = RoomModel.objects.create(
            name="Chambre libre",
            description="Disponible",
            capacity=4,
            price_per_night=Decimal("100.00"),
            available=True,
        )
        self.room_free.amenities.add(self.wifi, self.spa)

        self.room_booked = RoomModel.objects.create(
            name="Chambre reservee",
            description="Occupee",
            capacity=2,
            price_per_night=Decimal("80.00"),
            available=True,
        )
        self.room_booked.amenities.add(self.wifi)

        self.customer = CustomerModel.objects.create(
            first_name="Test",
            last_name="Client",
            email="client-rooms@example.com",
            phone="+33123456789",
            address="Paris",
        )

        Reservation.objects.create(
            client=self.customer,
            room=self.room_booked,
            check_in_date=self.check_in,
            check_out_date=self.check_out,
            guest_count=2,
            status="confirmed",
            total_price=Decimal("0.00"),
        )

    def api_get(self, url):
        return self.client.get(url, HTTP_HOST="localhost")

    def test_available_requires_dates(self):
        response = self.api_get("/api/rooms/rooms/available/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "Les paramètres check_in et check_out sont requis",
        )

    def test_available_returns_only_unbooked_rooms_with_total_price(self):
        response = self.api_get(
            f"/api/rooms/rooms/available/?check_in={self.check_in}&check_out={self.check_out}&guests=2"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["nights"], 3)
        self.assertEqual(payload["rooms"][0]["id"], self.room_free.id)
        self.assertEqual(payload["rooms"][0]["total_price"], 300.0)

    def test_availability_reports_conflicts(self):
        response = self.api_get(
            f"/api/rooms/rooms/{self.room_booked.id}/availability/?start_date={self.check_in}&end_date={self.check_out}"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["available"])
        self.assertEqual(len(payload["conflicting_reservations"]), 1)
        self.assertIsNone(payload["total_price"])

    def test_search_filters_by_dates_amenities_and_price(self):
        response = self.api_get(
            f"/api/rooms/rooms/search/?check_in={self.check_in}&check_out={self.check_out}&guests=2&amenities={self.wifi.id},{self.spa.id}&min_price=50&max_price=150"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["rooms"][0]["id"], self.room_free.id)
        self.assertEqual(payload["rooms"][0]["nights"], 3)
        self.assertEqual(payload["rooms"][0]["total_price"], 300.0)

    def test_calendar_rejects_invalid_months(self):
        response = self.api_get(f"/api/rooms/rooms/{self.room_booked.id}/calendar/?months=abc")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "Le paramètre months doit être un entier entre 1 et 12",
        )

    def test_calendar_returns_statistics(self):
        response = self.api_get(f"/api/rooms/rooms/{self.room_booked.id}/calendar/?months=1")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["statistics"]["booked_days"], 3)
        self.assertEqual(payload["statistics"]["available_days"], 28)
