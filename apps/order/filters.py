from django_filters.rest_framework import FilterSet

from apps.order.models import Order


class OrderFilter(FilterSet):
    class Meta:
        model = Order
        fields = {
            'order_date': ['gte', 'lte'],
        }
