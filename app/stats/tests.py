from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from app.rooms.models import RoomModel
from app.reservation.models import Reservation
from app.customers.models import CustomerModel
from app.reviews.models import Review
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

User = get_user_model()

class StatsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='password123'
        )
        
        # Create Room
        self.room = RoomModel.objects.create(
            name="Chambre Test",
            description="Description test",
            capacity=2,
            price_per_night=Decimal('100.00')
        )
        
        # Create Customer
        self.customer = CustomerModel.objects.create(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0123456789"
        )
        
        # Create Reservations
        # 1. Past completed reservation
        # 2. Confirmed current/future reservation
        # 3. Pending reservation
        
        # We use bulk_create to bypass the clean() method which prevents past dates
        reservations = [
            Reservation(
                room=self.room,
                client=self.customer,
                check_in_date=timezone.now().date() - timedelta(days=10),
                check_out_date=timezone.now().date() - timedelta(days=5),
                guest_count=2,
                status='completed',
                total_price=Decimal('500.00')
            ),
            Reservation(
                room=self.room,
                client=self.customer,
                check_in_date=timezone.now().date() + timedelta(days=1),
                check_out_date=timezone.now().date() + timedelta(days=4),
                guest_count=2,
                status='confirmed',
                total_price=Decimal('300.00')
            ),
            Reservation(
                room=self.room,
                client=self.customer,
                check_in_date=timezone.now().date() + timedelta(days=10),
                check_out_date=timezone.now().date() + timedelta(days=15),
                guest_count=2,
                status='pending',
                total_price=Decimal('500.00')
            )
        ]
        Reservation.objects.bulk_create(reservations)
        
        # Create Review
        Review.objects.create(
            room=self.room,
            client=self.customer,
            reservation=Reservation.objects.filter(status='completed').first(),
            rating=5,
            comment="Super chambre"
        )

    def test_stats_access_denied_for_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('stats-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stats_access_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('stats-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('stats-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_reservations'], 3)
        self.assertEqual(data['active_reservations'], 1)
        self.assertEqual(data['pending_reservations'], 1)
        self.assertEqual(data['completed_reservations'], 1)
        self.assertGreater(float(data['total_revenue']), 0)

    def test_reservations_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('stats-reservations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_occupancy_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('stats-occupancy')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rooms', response.data)
        self.assertGreater(len(response.data['rooms']), 0)

    def test_popular_rooms_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('stats-popular-rooms')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('popular_rooms', response.data)

    def test_revenue_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('stats-revenue')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
