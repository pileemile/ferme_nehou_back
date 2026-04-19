import django_filters
from .models import Activity


class ActivityFilter(django_filters.FilterSet):
    """Filtres pour les activités"""

    available = django_filters.BooleanFilter(
        field_name='available',
        label='Disponible'
    )

    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Prix minimum'
    )

    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Prix maximum'
    )

    class Meta:
        model = Activity
        fields = ['available', 'min_price', 'max_price']