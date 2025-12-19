import django_filters
from app.rooms.models import RoomModel, AmenityModel

class RoomFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price_per_night", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price_per_night", lookup_expr='lte')
    min_capacity = django_filters.NumberFilter(field_name="capacity", lookup_expr='gte')
    max_capacity = django_filters.NumberFilter(field_name="capacity", lookup_expr='lte')
    available = django_filters.BooleanFilter(field_name="available")
    amenities = django_filters.ModelMultipleChoiceFilter(field_name='amenities',queryset=AmenityModel.objects.all(),conjoined=True)

    class Meta:
        model = RoomModel
        fields = ['available', 'min_price', 'max_price', 'min_capacity', 'max_capacity']
