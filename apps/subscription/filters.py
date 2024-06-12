import django_filters

from apps.subscription.models import Subscription


class SubscriptionFilter(django_filters.FilterSet):
    start_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_to = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = Subscription
        fields = [
            'start_from',
            'start_to',
            'end_from',
            'end_to',
        ]
