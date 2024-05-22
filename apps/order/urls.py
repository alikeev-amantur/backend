from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PlaceOrderView, ClientOrderHistoryView, PartnerOrderHistoryView, PartnerPlaceOrderView, \
    OrderStatisticsView, IncomingOrdersView


router = DefaultRouter()
router.register(
    r"partner-order-history", PartnerOrderHistoryView, basename="partner-order-history"
)
router.register(
    r"client-order-history", ClientOrderHistoryView, basename="client-order-history"
)
urlpatterns = [
    path("place-order/", PlaceOrderView.as_view(), name="place-order"),
    path("partner-place-order/", PartnerPlaceOrderView.as_view(), name="partner-place-order"),
    path("statistics/<int:establishment_id>/", OrderStatisticsView.as_view(), name='order-statistics'),
    path("orders/", IncomingOrdersView.as_view(), name='incoming-orders'),
    path("", include(router.urls)),
]
