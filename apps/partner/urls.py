from django.urls import path

from .views import (
    EstablishmentListCreateView,
    EstablishmentViewSet,
    MenuView, PartnerEstablishmentView,
)

urlpatterns = [
    path(
        "establishments/",
        EstablishmentListCreateView.as_view(),
        name="establishments",
    ),
    path(
        "establishments/<int:pk>/",
        EstablishmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="establishment-detail",
    ),
    path("menu/<int:pk>/", MenuView.as_view({"get": "list"}), name="menu-list"),
    path("establishments/<int:partner_id>/", PartnerEstablishmentView.as_view(), name="partner-establishments")
]
