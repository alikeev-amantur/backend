from django_filters import rest_framework as filters

from apps.beverage.models import Beverage


class BeverageFilter(filters.FilterSet):
    # near_me = filters.NumberFilter(method='filter_near_me')
    establishment = filters.NumberFilter(field_name='establishment__id')
    category = filters.NumberFilter(field_name='category__id')
    availability_status = filters.BooleanFilter(field_name='availability_status')

    class Meta:
        model = Beverage
        fields = []