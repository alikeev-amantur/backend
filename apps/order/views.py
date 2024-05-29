from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.beverage.models import Beverage
from apps.order.filters import OrderFilter
from apps.order.models import Order
from apps.order.schema_definitions import order_request_body, place_order_responses, partner_place_order_request_body, \
    partner_place_order_responses, statistic_response, order_statistics_parameters
from apps.order.serializers import OrderSerializer, OrderHistorySerializer, OwnerOrderSerializer, \
    IncomingOrderSerializer
from apps.partner.models import Establishment
from apps.subscription.models import Subscription
from happyhours.permissions import IsPartnerUser

User = get_user_model()


@extend_schema(
    tags=["Orders"],
    request=order_request_body,
    responses=place_order_responses
)
class PlaceOrderView(generics.CreateAPIView):
    """
    API endpoint for placing orders. Only authenticated users can create orders.

    The endpoint expects beverage ID as part of the request, and automatically sets the order's client
    to the current user and the establishment to the one associated with the specified beverage.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if not self.user_has_active_subscription(user):
            raise PermissionDenied("You need an active subscription to place an order.")

        beverage_id = serializer.validated_data.get("beverage").id
        beverage = Beverage.objects.get(id=beverage_id)
        serializer.save(client=user, establishment=beverage.establishment)

    def user_has_active_subscription(self, user):
        return Subscription.objects.filter(user=user, is_active=True).exists()


@extend_schema(tags=["Orders"], responses={200: OrderHistorySerializer})
class ClientOrderHistoryView(ReadOnlyModelViewSet):
    """
    ViewSet for viewing a client's own order history.
    Provides endpoints for listing all orders associated
    with the authenticated client and for retrieving details of a specific order.
    """

    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user).select_related(
            'establishment', 'beverage', 'client'
        )


@extend_schema(tags=["Orders"], responses={200: OrderHistorySerializer})
class PartnerOrderHistoryView(generics.ListAPIView):
    """
    ViewSet for viewing order history for partners.
    Lists all orders related to establishments owned by the authenticated partner and
    allows retrieving specific orders.

    This viewset supports listing all such orders and retrieving details for a specific order.
    """

    serializer_class = OrderHistorySerializer
    permission_classes = [IsPartnerUser]

    def get_queryset(self):
        """
        This queryset returns orders for the establishments owned by the logged-in user.
        """
        establishment_id = self.kwargs['establishment_id']
        establishment = Establishment.objects.get(id=establishment_id)

        if establishment.owner != self.request.user:
            raise PermissionDenied("You do not have permission to view these orders.")
        return Order.objects.filter(establishment=establishment, status='completed')


@extend_schema(
    tags=["Orders"],
    request=partner_place_order_request_body,
    responses=partner_place_order_responses
)
class PartnerPlaceOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OwnerOrderSerializer
    permission_classes = [IsPartnerUser]

    def perform_create(self, serializer):
        beverage = serializer.validated_data['beverage']
        establishment = beverage.establishment
        client = serializer.validated_data['client']

        if self.request.user != establishment.owner:
            raise PermissionDenied({
                'error': 'You are not the owner of the establishment linked to this beverage.'
            })

        if not self.user_has_active_subscription(client):
            raise PermissionDenied({
                'error': "Client doesn't have an active subscription"
            })

        serializer.save(establishment=establishment, client=client)

    def user_has_active_subscription(self, user):
        return Subscription.objects.filter(user=user, is_active=True).exists()


@extend_schema(tags=["Orders"], parameters=order_statistics_parameters, responses=statistic_response)
class OrderStatisticsView(generics.ListAPIView):
    permission_classes = [IsPartnerUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_queryset(self):
        establishment_id = self.kwargs['establishment_id']
        establishment = Establishment.objects.get(id=establishment_id)
        return Order.objects.filter(establishment=establishment)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        total_orders = self.get_total_orders(queryset)
        orders_by_category = self.get_orders_by_category(queryset)

        data = {
            'total_orders': total_orders,
            'orders_by_category': orders_by_category,
        }

        return Response(data)

    def get_total_orders(self, queryset):
        total_orders = queryset.count()
        return total_orders

    def get_orders_by_category(self, queryset):
        orders_by_category = (
            queryset.values('beverage__category__name')
            .annotate(total_orders=Count('id'))
            .order_by('beverage__category__name')
        )
        return [
            {'category': stat['beverage__category__name'], 'total_orders': stat['total_orders']}
            for stat in orders_by_category
        ]


@extend_schema(tags=["Orders"])
class IncomingOrdersView(generics.ListAPIView):
    serializer_class = IncomingOrderSerializer
    permission_classes = [IsPartnerUser]

    def get_queryset(self):
        establishment_id = self.kwargs['establishment_id']
        establishment = Establishment.objects.get(id=establishment_id)

        if establishment.owner != self.request.user:
            raise PermissionDenied("You do not have permission to view these orders.")

        return Order.objects.filter(
            establishment=establishment,
            status__in=['pending', 'in_preparation']
        )
