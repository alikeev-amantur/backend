import django_filters

from .models import Establishment


class EstablishmentFilter(django_filters.FilterSet):
    location = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Establishment
        fields = (
            'location',
        )
