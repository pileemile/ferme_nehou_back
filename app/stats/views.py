from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from app.reservation.models import Reservation
from app.customers.models import CustomerModel
from app.reviews.models import Review
from app.rooms.models import RoomModel
from .serializers import (
    DashboardStatsSerializer,
    ReservationStatsSerializer,
    OccupancyStatsSerializer,
    PopularRoomSerializer,
    RevenueStatsSerializer,
)


class StatsViewSet(ViewSet):
    """ViewSet pour les statistiques admin"""
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        GET /api/admin/stats/dashboard/

        Statistiques générales du dashboard
        """
        # Statistiques des réservations
        total_reservations = Reservation.objects.count()
        active_reservations = Reservation.objects.filter(
            status='confirmed',
            check_out_date__gte=timezone.now().date()
        ).count()
        pending_reservations = Reservation.objects.filter(status='pending').count()
        completed_reservations = Reservation.objects.filter(status='completed').count()
        cancelled_reservations = Reservation.objects.filter(status='canceled').count()

        # Chiffre d'affaires
        total_revenue = Reservation.objects.filter(
            status__in=['confirmed', 'completed']
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')

        # CA du mois en cours
        first_day_of_month = timezone.now().date().replace(day=1)
        current_month_revenue = Reservation.objects.filter(
            status__in=['confirmed', 'completed'],
            created_at__gte=first_day_of_month
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')

        # Clients et avis
        total_customers = CustomerModel.objects.count()
        total_reviews = Review.objects.count()
        average_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0

        # Taux d'occupation global (30 derniers jours)
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
        total_days = 30 * RoomModel.objects.count()

        booked_days = 0
        for room in RoomModel.objects.all():
            reservations = Reservation.objects.filter(
                room=room,
                status__in=['confirmed', 'completed'],
                check_in_date__lte=end_date,
                check_out_date__gte=start_date
            )

            for res in reservations:
                # Calculer le chevauchement avec la période
                overlap_start = max(res.check_in_date, start_date)
                overlap_end = min(res.check_out_date, end_date)
                if overlap_start < overlap_end:
                    booked_days += (overlap_end - overlap_start).days

        occupancy_rate = round((booked_days / total_days * 100), 2) if total_days > 0 else 0

        data = {
            'total_reservations': total_reservations,
            'active_reservations': active_reservations,
            'pending_reservations': pending_reservations,
            'completed_reservations': completed_reservations,
            'cancelled_reservations': cancelled_reservations,
            'total_revenue': total_revenue,
            'current_month_revenue': current_month_revenue,
            'total_customers': total_customers,
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2),
            'occupancy_rate': occupancy_rate,
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reservations(self, request):
        """
        GET /api/admin/stats/reservations/?period=month&year=2025

        Statistiques des réservations par période
        Paramètres:
        - period: day, week, month, year (défaut: month)
        - year: année (défaut: année en cours)
        - month: mois (optionnel, pour period=day)
        """
        period = request.query_params.get('period', 'month')
        year = int(request.query_params.get('year', timezone.now().year))
        month = request.query_params.get('month')

        results = []

        if period == 'month':
            # Statistiques par mois pour l'année
            for m in range(1, 13):
                start_date = datetime(year, m, 1).date()
                if m == 12:
                    end_date = datetime(year + 1, 1, 1).date()
                else:
                    end_date = datetime(year, m + 1, 1).date()

                reservations = Reservation.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date,
                    status__in=['confirmed', 'completed']
                )

                count = reservations.count()
                revenue = reservations.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
                avg_value = revenue / count if count > 0 else Decimal('0.00')

                results.append({
                    'period': f'{year}-{m:02d}',
                    'reservations_count': count,
                    'revenue': revenue,
                    'average_booking_value': avg_value,
                })

        elif period == 'year':
            # Statistiques par année (5 dernières années)
            current_year = timezone.now().year
            for y in range(current_year - 4, current_year + 1):
                reservations = Reservation.objects.filter(
                    created_at__year=y,
                    status__in=['confirmed', 'completed']
                )

                count = reservations.count()
                revenue = reservations.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
                avg_value = revenue / count if count > 0 else Decimal('0.00')

                results.append({
                    'period': str(y),
                    'reservations_count': count,
                    'revenue': revenue,
                    'average_booking_value': avg_value,
                })

        elif period == 'week':
            # Statistiques par semaine (12 dernières semaines)
            for week in range(12):
                end_date = timezone.now().date() - timedelta(weeks=week)
                start_date = end_date - timedelta(days=7)

                reservations = Reservation.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date,
                    status__in=['confirmed', 'completed']
                )

                count = reservations.count()
                revenue = reservations.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
                avg_value = revenue / count if count > 0 else Decimal('0.00')

                results.append({
                    'period': f'Semaine du {start_date}',
                    'reservations_count': count,
                    'revenue': revenue,
                    'average_booking_value': avg_value,
                })

            results.reverse()

        serializer = ReservationStatsSerializer(results, many=True)
        return Response({
            'period_type': period,
            'year': year,
            'data': serializer.data,
        })

    @action(detail=False, methods=['get'])
    def occupancy(self, request):
        """
        GET /api/admin/stats/occupancy/?days=30

        Taux d'occupation par chambre
        Paramètres:
        - days: nombre de jours à analyser (défaut: 30)
        """
        days = int(request.query_params.get('days', 30))

        start_date = timezone.now().date() - timedelta(days=days)
        end_date = timezone.now().date()

        results = []

        for room in RoomModel.objects.all():
            # Compter les jours réservés
            booked_days = 0
            reservations = Reservation.objects.filter(
                room=room,
                status__in=['confirmed', 'completed'],
                check_in_date__lte=end_date,
                check_out_date__gte=start_date
            )

            for res in reservations:
                # Calculer le chevauchement avec la période
                overlap_start = max(res.check_in_date, start_date)
                overlap_end = min(res.check_out_date, end_date)
                if overlap_start < overlap_end:
                    booked_days += (overlap_end - overlap_start).days

            occupancy_rate = round((booked_days / days * 100), 2)

            results.append({
                'room_id': room.id,
                'room_name': room.name,
                'total_days': days,
                'booked_days': booked_days,
                'available_days': days - booked_days,
                'occupancy_rate': occupancy_rate,
            })

        # Trier par taux d'occupation décroissant
        results.sort(key=lambda x: x['occupancy_rate'], reverse=True)

        serializer = OccupancyStatsSerializer(results, many=True)

        # Calculer le taux global
        total_booked = sum(r['booked_days'] for r in results)
        total_days = days * len(results)
        global_rate = round((total_booked / total_days * 100), 2) if total_days > 0 else 0

        return Response({
            'period_days': days,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'global_occupancy_rate': global_rate,
            'rooms': serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='popular-rooms')
    def popular_rooms(self, request):
        """
        GET /api/admin/stats/popular-rooms/?limit=5

        Chambres les plus réservées
        Paramètres:
        - limit: nombre de chambres à retourner (défaut: 5)
        """
        limit = int(request.query_params.get('limit', 5))

        # Agréger les statistiques par chambre
        rooms_stats = RoomModel.objects.annotate(
            reservations_count=Count(
                'reservations',
                filter=Q(reservations__status__in=['confirmed', 'completed'])
            ),
            total_revenue=Sum(
                'reservations__total_price',
                filter=Q(reservations__status__in=['confirmed', 'completed'])
            ),
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        ).order_by('-reservations_count')[:limit]

        results = []
        for room in rooms_stats:
            results.append({
                'room_id': room.id,
                'room_name': room.name,
                'reservations_count': room.reservations_count,
                'total_revenue': room.total_revenue or Decimal('0.00'),
                'average_rating': round(room.avg_rating, 2) if room.avg_rating else 0,
                'total_reviews': room.reviews_count,
            })

        serializer = PopularRoomSerializer(results, many=True)
        return Response({
            'limit': limit,
            'popular_rooms': serializer.data,
        })

    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """
        GET /api/admin/stats/revenue/?period=month&year=2025

        Chiffre d'affaires détaillé
        Paramètres:
        - period: month, quarter, year (défaut: month)
        - year: année (défaut: année en cours)
        """
        period = request.query_params.get('period', 'month')
        year = int(request.query_params.get('year', timezone.now().year))

        results = []

        if period == 'month':
            # CA par mois
            for m in range(1, 13):
                start_date = datetime(year, m, 1).date()
                if m == 12:
                    end_date = datetime(year + 1, 1, 1).date()
                else:
                    end_date = datetime(year, m + 1, 1).date()

                reservations = Reservation.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date,
                    status__in=['confirmed', 'completed']
                )

                count = reservations.count()
                revenue = reservations.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
                avg_value = revenue / count if count > 0 else Decimal('0.00')

                results.append({
                    'period': f'{year}-{m:02d}',
                    'total_revenue': revenue,
                    'reservations_count': count,
                    'average_booking_value': avg_value,
                })

        elif period == 'quarter':
            # CA par trimestre
            quarters = [
                (1, 'Q1'),
                (4, 'Q2'),
                (7, 'Q3'),
                (10, 'Q4'),
            ]

            for start_month, quarter_name in quarters:
                start_date = datetime(year, start_month, 1).date()
                end_month = start_month + 3
                if end_month > 12:
                    end_date = datetime(year + 1, end_month - 12, 1).date()
                else:
                    end_date = datetime(year, end_month, 1).date()

                reservations = Reservation.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date,
                    status__in=['confirmed', 'completed']
                )

                count = reservations.count()
                revenue = reservations.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
                avg_value = revenue / count if count > 0 else Decimal('0.00')

                results.append({
                    'period': f'{year} {quarter_name}',
                    'total_revenue': revenue,
                    'reservations_count': count,
                    'average_booking_value': avg_value,
                })

        elif period == 'year':
            # CA par année (5 dernières années)
            current_year = timezone.now().year
            for y in range(current_year - 4, current_year + 1):
                reservations = Reservation.objects.filter(
                    created_at__year=y,
                    status__in=['confirmed', 'completed']
                )

                count = reservations.count()
                revenue = reservations.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
                avg_value = revenue / count if count > 0 else Decimal('0.00')

                results.append({
                    'period': str(y),
                    'total_revenue': revenue,
                    'reservations_count': count,
                    'average_booking_value': avg_value,
                })

        serializer = RevenueStatsSerializer(results, many=True)

        # Calculer le total
        total_revenue = sum(r['total_revenue'] for r in results)
        total_reservations = sum(r['reservations_count'] for r in results)

        return Response({
            'period_type': period,
            'year': year,
            'total_revenue': total_revenue,
            'total_reservations': total_reservations,
            'average_booking_value': total_revenue / total_reservations if total_reservations > 0 else Decimal('0.00'),
            'data': serializer.data,
        })


from django.shortcuts import render

# Create your views here.
