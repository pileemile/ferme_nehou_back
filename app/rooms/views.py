from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count, Prefetch
from django.utils.decorators import method_decorator
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django_ratelimit.decorators import ratelimit
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from app.cache import invalidate_room_cache, make_cache_key
from app.pagination import CustomPageNumberPagination, SmallResultsSetPagination
from app.permissions import IsAdminUser
from app.reservation.models import Reservation
from app.reviews.models import Review
from app.reviews.serializers import SerializerReviews
from app.rooms.filter import RoomFilter
from app.rooms.models import RoomModel
from app.rooms.serializers import AmenitySerializer, SerializerRooms, SerializerRoomsDetail

class RoomViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = SerializerRooms
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        public_actions = {
            "list",
            "retrieve",
            "search",
            "available",
            "availability",
            "calendar",
            "average_rating",
            "reviews",
            "amenities",
            "featured",
        }
        if self.action in public_actions:
            return []
        return [IsAdminUser()]

    def get_queryset(self):
        return RoomModel.objects.all().prefetch_related(
            Prefetch("amenities"),
            Prefetch("photos"),
            Prefetch(
                "reviews",
                queryset=Review.objects.select_related("client").order_by("-created_at"),
            ),
        )

    def list(self, request, *args, **kwargs):
        """
        GET /api/rooms/?page=1&page_size=10
        Liste des chambres mise en cache selon les paramètres de requête.
        """
        cache_key = make_cache_key("rooms_list", dict(request.query_params))
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        if response.status_code == 200:
            cache.set(cache_key, response.data, settings.CACHE_TTL_ROOMS)

        return response

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/rooms/{id}/
        Détail complet d'une chambre mis en cache par ID.
        """
        room_id = kwargs.get("pk")
        cache_key = f"room_detail_{room_id}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        instance = self.get_object()
        serializer = SerializerRoomsDetail(instance, context={"request": request})
        data = serializer.data

        cache.set(cache_key, data, settings.CACHE_TTL_ROOMS)
        return Response(data)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_room_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_room_cache(room_id=serializer.instance.id)

    def perform_destroy(self, instance):
        room_id = instance.id
        super().perform_destroy(instance)
        invalidate_room_cache(room_id=room_id)

    @method_decorator(ratelimit(key="ip", rate="100/h", method="GET", block=True))
    @action(detail=False, methods=["get"])
    def available(self, request):
        """
        Endpoint: GET /api/rooms/available/?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&guests=2

        Retourne les chambres disponibles pour les dates données avec le prix total
        """
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        guests = request.query_params.get("guests")

        # Validation des paramètres obligatoires
        if not check_in or not check_out:
            return Response(
                {
                    "error": "Les paramètres check_in et check_out sont requis",
                    "format": "YYYY-MM-DD",
                    "example": "/api/rooms/available/?check_in=2025-12-10&check_out=2025-12-15&guests=2",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parser les dates
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {
                    "error": "Format de date invalide. Utilisez YYYY-MM-DD",
                    "example": "2025-12-10",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validations logiques
        if check_out_date <= check_in_date:
            return Response(
                {"error": "La date de départ doit être après la date d'arrivée"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if check_in_date < timezone.now().date():
            return Response(
                {"error": "La date d'arrivée ne peut pas être dans le passé"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Commencer avec toutes les chambres
        queryset = self.get_queryset()

        # Filtrer par capacité si spécifié
        if guests:
            try:
                guests_count = int(guests)
                queryset = queryset.filter(capacity__gte=guests_count)
            except (ValueError, TypeError):
                pass

        # Trouver les chambres avec réservations qui chevauchent
        unavailable_rooms = Reservation.objects.filter(
            status__in=["pending", "confirmed"],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
        ).values_list("room_id", flat=True)

        # Exclure ces chambres
        available_rooms = queryset.exclude(id__in=unavailable_rooms)

        # Calculer le nombre de nuits
        nights = (check_out_date - check_in_date).days

        # Sérialiser
        page = self.paginate_queryset(available_rooms)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            results = []
            for room_data in serializer.data:
                room_data["nights"] = nights
                room_data["total_price"] = float(room_data["price_per_night"]) * nights
                room_data["check_in"] = check_in
                room_data["check_out"] = check_out
                results.append(room_data)
            return self.get_paginated_response(results)

        serializer = self.get_serializer(available_rooms, many=True)

        # Ajouter infos supplémentaires à chaque chambre
        results = []
        for room_data in serializer.data:
            room_data["nights"] = nights
            room_data["total_price"] = float(room_data["price_per_night"]) * nights
            room_data["check_in"] = check_in
            room_data["check_out"] = check_out
            results.append(room_data)

        return Response(
            {
                "check_in": check_in,
                "check_out": check_out,
                "nights": nights,
                "guests": guests,
                "count": len(results),
                "rooms": results,
            }
        )

    # ========================================
    # AMÉLIORATION: Endpoint availability
    # ========================================
    @action(detail=True, methods=["get"])
    def availability(self, request, pk=None):
        """
        Endpoint: GET /api/rooms/{id}/availability/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD

        Vérifier la disponibilité d'une chambre pour des dates données
        Amélioré avec calcul du prix total
        """
        room = self.get_object()

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response(
                {"error": "Les paramètres start_date et end_date sont obligatoires"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Format de la date incorrect. Utilisez YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validation logique
        if end_date <= start_date:
            return Response(
                {"error": "La date de fin doit être après la date de début"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifier les conflits
        conflicting = Reservation.objects.filter(
            room=room,
            status__in=["pending", "confirmed"],
            check_in_date__lt=end_date,
            check_out_date__gt=start_date,
        )

        available = not conflicting.exists()

        conflicting_data = []
        if not available:
            for res in conflicting:
                conflicting_data.append(
                    {
                        "id": res.id,
                        "check_in": res.check_in_date.strftime("%Y-%m-%d"),
                        "check_out": res.check_out_date.strftime("%Y-%m-%d"),
                        "status": res.status,
                    }
                )

        # Calcul du prix
        nights = (end_date - start_date).days

        return Response(
            {
                "room_id": room.id,
                "room_name": room.name,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "nights": nights,
                "available": available,
                "price_per_night": float(room.price_per_night),
                "total_price": float(room.price_per_night) * nights if available else None,
                "conflicting_reservations": conflicting_data,
            }
        )

    # ========================================
    # AMÉLIORATION: Endpoint search
    # ========================================
    @method_decorator(ratelimit(key="ip", rate="50/h", method="GET", block=True))
    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Endpoint: GET /api/rooms/search/?check_in=&check_out=&guests=&min_price=&max_price=&amenities=1,2,3

        Recherche avancée combinant disponibilité et filtres
        Amélioré avec support des amenities et calcul du prix total
        """
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        guests = request.query_params.get("guests")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        amenities = request.query_params.get("amenities")  # ← NOUVEAU

        cache_key = None
        if not check_in and not check_out:
            cache_key = make_cache_key(
                "rooms_search",
                {
                    "guests": guests,
                    "min_price": min_price,
                    "max_price": max_price,
                    "amenities": amenities,
                    "page": request.query_params.get("page"),
                    "page_size": request.query_params.get("page_size"),
                },
            )
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

        queryset = self.get_queryset()

        # Filtrer par capacité
        if guests:
            try:
                queryset = queryset.filter(capacity__gte=int(guests))
            except (ValueError, TypeError):
                pass

        # Filtrer par prix
        if min_price:
            try:
                queryset = queryset.filter(price_per_night__gte=float(min_price))
            except (ValueError, TypeError):
                pass

        if max_price:
            try:
                queryset = queryset.filter(price_per_night__lte=float(max_price))
            except (ValueError, TypeError):
                pass

        # Filtrer par équipements (NOUVEAU)
        if amenities:
            try:
                amenity_ids = [int(id.strip()) for id in amenities.split(",")]
                for amenity_id in amenity_ids:
                    queryset = queryset.filter(amenities__id=amenity_id)
                queryset = queryset.distinct()
            except (ValueError, TypeError):
                pass

        # Filtrer par disponibilité sur les dates
        nights = None
        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
                check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

                if check_out_date > check_in_date and check_in_date >= timezone.now().date():
                    unavailable_rooms = Reservation.objects.filter(
                        status__in=["pending", "confirmed"],
                        check_in_date__lt=check_out_date,
                        check_out_date__gt=check_in_date,
                    ).values_list("room_id", flat=True)

                    queryset = queryset.exclude(id__in=unavailable_rooms)
                    nights = (check_out_date - check_in_date).days

            except ValueError:
                return Response(
                    {"error": "Format de date invalide. Utilisez YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            results = []
            for room_data in serializer.data:
                if nights:
                    room_data["nights"] = nights
                    room_data["total_price"] = float(room_data["price_per_night"]) * nights
                results.append(room_data)

            response = self.get_paginated_response(results)
            if cache_key and response.status_code == 200:
                cache.set(cache_key, response.data, settings.CACHE_TTL_ROOMS)
            return response

        serializer = self.get_serializer(queryset, many=True)

        data = {
            "filters": {
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "min_price": min_price,
                "max_price": max_price,
                "amenities": amenities,
            },
            "count": queryset.count(),
            "rooms": serializer.data,
        }

        if nights:
            rooms = []
            for room_data in data["rooms"]:
                room_data["nights"] = nights
                room_data["total_price"] = float(room_data["price_per_night"]) * nights
                rooms.append(room_data)
            data["rooms"] = rooms

        if cache_key:
            cache.set(cache_key, data, settings.CACHE_TTL_ROOMS)

        return Response(data)

    # ========================================
    # AMÉLIORATION: Endpoint calendar
    # ========================================
    @action(detail=True, methods=["get"])
    def calendar(self, request, pk=None):
        """
        Endpoint: GET /api/rooms/{id}/calendar/?months=3

        Retourne le calendrier de disponibilité d'une chambre
        Amélioré avec calendrier jour par jour et statistiques
        """
        room = self.get_object()

        # Nombre de mois à afficher (par défaut 3, max 12)
        try:
            months = int(request.query_params.get("months", 3))
        except (TypeError, ValueError):
            return Response(
                {"error": "Le paramètre months doit être un entier entre 1 et 12"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if months > 12:
            months = 12
        if months < 1:
            months = 1

        # Date de début et fin
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30 * months)

        # Récupérer toutes les réservations pour cette période
        reservations = Reservation.objects.filter(
            room=room,
            status__in=["pending", "confirmed"],
            check_in_date__lte=end_date,
            check_out_date__gte=start_date,
        ).order_by("check_in_date")

        # Formater les réservations
        calendar_data = []
        for res in reservations:
            calendar_data.append(
                {
                    "id": res.id,
                    "check_in": res.check_in_date.strftime("%Y-%m-%d"),
                    "check_out": res.check_out_date.strftime("%Y-%m-%d"),
                    "status": res.status,
                    "guest_count": res.guest_count,
                    "nights": res.get_number_of_nights(),
                }
            )

        # Générer le calendrier jour par jour (NOUVEAU)
        date_status = {}
        current_date = start_date

        while current_date <= end_date:
            # Vérifier si cette date est dans une réservation
            is_available = True
            for res in reservations:
                if res.check_in_date <= current_date < res.check_out_date:
                    is_available = False
                    break

            date_status[current_date.strftime("%Y-%m-%d")] = {
                "available": is_available,
                "price": float(room.price_per_night),
            }

            current_date += timedelta(days=1)

        # Calculer les statistiques (NOUVEAU)
        total_days = len(date_status)
        available_days = sum(1 for d in date_status.values() if d["available"])
        booked_days = total_days - available_days
        occupancy_rate = round((booked_days / total_days) * 100, 2) if total_days > 0 else 0

        return Response(
            {
                "room_id": room.id,
                "room_name": room.name,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "reservations": calendar_data,
                "calendar": date_status,
                "statistics": {
                    "total_days": total_days,
                    "available_days": available_days,
                    "booked_days": booked_days,
                    "occupancy_rate": occupancy_rate,
                },
            }
        )

    # ========================================
    # Endpoints existants (inchangés)
    # ========================================
    @action(detail=True, methods=["get"])
    def average_rating(self, request, pk=None):
        """Obtenir la note moyenne d'une chambre"""
        room = self.get_object()

        stats = Review.objects.filter(room=room).aggregate(
            average=Avg("rating"),
            total=Count("rating"),
        )
        return Response(
            {
                "room_id": room.id,
                "room_name": room.name,
                "average_rating": round(stats["average"], 2) if stats["average"] else None,
                "total_reviews": stats["total"],
            }
        )

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        """Obtenir tous les avis d'une chambre"""
        room = self.get_object()
        reviews = Review.objects.filter(room=room).select_related(
            "client",
            "reservation",
        ).order_by("-created_at")

        self.pagination_class = SmallResultsSetPagination
        page = self.paginate_queryset(reviews)

        if page is not None:
            serializer = SerializerReviews(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = SerializerReviews(reviews, many=True, context={"request": request})
        return Response(
            {
                "room_id": room.id,
                "room_name": room.name,
                "total_reviews": reviews.count(),
                "reviews": serializer.data,
            }
        )

    @action(detail=True, methods=["get"])
    def amenities(self, request, pk=None):
        """Obtenir les équipements d'une chambre"""
        room = self.get_object()
        amenities = room.amenities.all()
        serializer = AmenitySerializer(amenities, many=True)
        return Response(
            {
                "room_id": room.id,
                "room_name": room.name,
                "amenities": serializer.data,
            }
        )

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        GET /api/rooms/featured/?limit=3
        Chambres mises en avant mises en cache.
        """
        try:
            limit = int(request.query_params.get("limit", 3))
        except (TypeError, ValueError):
            limit = 3
        if limit > 10:
            limit = 10
        if limit < 1:
            limit = 1

        cache_key = f"rooms_featured_{limit}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        photo_model = RoomModel._meta.get_field("photos").related_model
        featured_rooms = RoomModel.objects.filter(
            available=True
        ).annotate(
            avg_rating=Avg("reviews__rating"),
            reviews_count=Count("reviews"),
        ).prefetch_related(
            "amenities",
            Prefetch("photos", queryset=photo_model.objects.order_by("order")),
            Prefetch(
                "reviews",
                queryset=Review.objects.select_related("client").order_by("-created_at"),
            ),
        ).order_by(
            "-avg_rating",
            "-reviews_count",
        )[:limit]

        serializer = SerializerRoomsDetail(
            featured_rooms,
            many=True,
            context={"request": request},
        )
        data = {"count": len(serializer.data), "featured_rooms": serializer.data}

        cache.set(cache_key, data, settings.CACHE_TTL_FEATURED)
        return Response(data)
