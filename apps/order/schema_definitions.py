from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, inline_serializer, extend_schema, OpenApiParameter
from rest_framework import serializers

from apps.order.serializers import OrderSerializer, OwnerOrderSerializer

order_request_body = inline_serializer(
    name='OrderRequest',
    fields={
        'beverage': serializers.IntegerField(),
    }
)

partner_place_order_request_body = inline_serializer(
    name='PartnerOrderRequest',
    fields={
        'beverage': serializers.IntegerField(),
        'client_email': serializers.EmailField(),
    }
)

place_order_responses = {
    201: OpenApiResponse(
        response=OrderSerializer,
        description="Order placed successfully."
    ),
    400: OpenApiResponse(
        description="Validation error.",
        examples={
            'non_field_errors': [
                "Order can only be placed during happy hours.",
                "You can only place one order per hour.",
                "You can only place one order per establishment per day."
            ]
        }
    ),
}

partner_place_order_responses = {
    201: OpenApiResponse(
        response=OwnerOrderSerializer,
        description="Order placed successfully by partner."
    ),
    400: OpenApiResponse(
        description="Validation error.",
        examples={
            'client_email': [
                "No user found with this email address."
            ],
            'non_field_errors': [
                "Order can only be placed during happy hours.",
                "You can only place one order per hour.",
                "You can only place one order per establishment per day."
            ]
        }
    ),
    403: OpenApiResponse(
        description="Permission denied.",
        examples={'error': 'You are not the owner of the establishment linked to this beverage.'}
    ),
}

statistic_response = {
    200: OpenApiResponse(
        response=inline_serializer(
            name='OrderStatisticsResponse',
            fields={
                'total_orders': serializers.IntegerField(),
                'total_sum_prices': serializers.DecimalField(max_digits=10, decimal_places=2),
                'orders_by_category': serializers.ListField(
                    child=inline_serializer(
                        name='OrderByCategory',
                        fields={
                            'category': serializers.CharField(),
                            'total_orders': serializers.IntegerField(),
                        }
                    )
                ),
            }
        ),
        description="Order statistics by establishment"
    )}
order_statistics_parameters = [
    OpenApiParameter(
        name='order_date__gte',
        description='Filter orders by order date greater than or equal to a specific date',
        required=False,
        type=OpenApiTypes.DATE,
        location=OpenApiParameter.QUERY
    ),
    OpenApiParameter(
        name='order_date__lte',
        description='Filter orders by order date less than or equal to a specific date',
        required=False,
        type=OpenApiTypes.DATE,
        location=OpenApiParameter.QUERY
    )
]
