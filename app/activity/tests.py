from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from app.activity.models import Activity


class ActivityEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.admin = self.user_model.objects.create_superuser(
            email="admin-activity@example.com",
            username="adminactivity",
            password="Admin12345!",
        )

        self.available_activity = Activity.objects.create(
            name="Kayak",
            description="Disponible",
            price=Decimal("25.00"),
            available=True,
        )
        Activity.objects.create(
            name="Escalade",
            description="Indisponible",
            price=Decimal("40.00"),
            available=False,
        )

    def api_get(self, url):
        return self.client.get(url, HTTP_HOST="localhost")

    def test_available_requires_authentication(self):
        response = self.api_get("/api/activity/available/")

        self.assertEqual(response.status_code, 401)

    def test_available_rejects_invalid_date(self):
        self.client.force_authenticate(user=self.admin)

        response = self.api_get("/api/activity/available/?date=2026-99-99")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "Format de date invalide. Utilisez YYYY-MM-DD",
        )

    def test_available_returns_only_available_activities(self):
        self.client.force_authenticate(user=self.admin)

        response = self.api_get("/api/activity/available/?date=2026-12-10")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["activities"][0]["id"], self.available_activity.id)

    def test_check_availability_requires_date(self):
        self.client.force_authenticate(user=self.admin)

        response = self.api_get(
            f"/api/activity/{self.available_activity.id}/check_availability/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Le paramètre date est requis")

    def test_check_availability_returns_total_price(self):
        self.client.force_authenticate(user=self.admin)

        response = self.api_get(
            f"/api/activity/{self.available_activity.id}/check_availability/?date=2026-12-10&quantity=3"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["available"])
        self.assertEqual(payload["total_price"], 75.0)
