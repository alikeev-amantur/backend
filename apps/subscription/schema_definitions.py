from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, inline_serializer, \
    OpenApiParameter
from rest_framework import serializers

# Custom response definitions
deactivate_subscription_responses = {
    200: OpenApiResponse(
        description="Subscription deactivated successfully.",
        examples={'detail': 'Subscription deactivated successfully.'}
    ),
    403: OpenApiResponse(
        description="Not allowed to deactivate this subscription.",
        examples={'detail': 'Not allowed to deactivate this subscription.'}
    ),
    400: OpenApiResponse(
        description="Subscription is already deactivated.",
        examples={'detail': 'Subscription is already deactivated.'}
    ),
}

free_trial_responses = {
    200: OpenApiResponse(
        description="Free trial activated successfully.",
        examples={
            'status': 'Free trial activated',
            'subscription_id': 1,
            'end_date': '2023-12-31T23:59:59Z'
        }
    ),
    400: OpenApiResponse(
        description="Validation error.",
        examples={'error': 'User has already used a free trial for this plan'}
    ),
}

free_trial_request_body = inline_serializer(
    name='FreeTrialRequest',
    fields={
        'plan_id': serializers.IntegerField()
    }
)

subscription_statistics_parameters = [
    OpenApiParameter(
        name='start_from',
        description='Filter for subscription statistic. Greater than or equal',
        required=False,
        type=OpenApiTypes.DATE,
        location=OpenApiParameter.QUERY
    ),
    OpenApiParameter(
        name='start_to',
        description='Filter for subscription statistic. Less than or equal',
        required=False,
        type=OpenApiTypes.DATE,
        location=OpenApiParameter.QUERY
    ),
    OpenApiParameter(
        name='end_to',
        description='Filter for subscription statistic. Less than or equal',
        required=False,
        type=OpenApiTypes.DATE,
        location=OpenApiParameter.QUERY
    ),
    OpenApiParameter(
        name='end_from',
        description='Filter for subscription statistic. Greater than or equal',
        required=False,
        type=OpenApiTypes.DATE,
        location=OpenApiParameter.QUERY
    )
]

