import django_filters
from app.rooms.models import RoomModel, AmenityModel

class RoomFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price_per_night", lookup_expr='gte', label='Prix minimum')
    max_price = django_filters.NumberFilter(field_name="price_per_night", lookup_expr='lte', label='Prix maximum')
    min_capacity = django_filters.NumberFilter(field_name="capacity", lookup_expr='gte', label='Capacité minimale')
    max_capacity = django_filters.NumberFilter(field_name="capacity", lookup_expr='lte', label='Capacité maximale')
    available = django_filters.BooleanFilter(field_name="available", label='Disponible')
    amenities = django_filters.ModelMultipleChoiceFilter(field_name='amenities',queryset=AmenityModel.objects.all(),conjoined=True, label='Équipements (IDs séparés par des virgules)')

    class Meta:
        model = RoomModel
        fields = ['available', 'min_price', 'max_price', 'min_capacity', 'max_capacity']

        def filter_by_amenities(self, queryset, name, value):
            """
            Filtre les chambres ayant TOUS les équipements demandés
            Format: ?amenities=1,2,3
            """
            if not value:
                return queryset

            try:
                # Convertir la chaîne en liste d'IDs
                amenity_ids = [int(id.strip()) for id in value.split(',')]

                # Filtrer les chambres ayant TOUS ces équipements
                for amenity_id in amenity_ids:
                    queryset = queryset.filter(amenities__id=amenity_id)

                return queryset.distinct()
            except (ValueError, TypeError):
                return queryset