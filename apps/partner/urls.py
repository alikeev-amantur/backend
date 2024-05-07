from django.urls import path

from .views import (
    EstablishmentListView,
    EstablishmentCreateView,
    EstablishmentViewSet,
    MenuView,
)
from ..feedback.views import FeedbackListView, FeedbackCreateView

urlpatterns = [
    path("establishment/list/", EstablishmentListView.as_view(), name='establishment-list'),
    path("establishment/create/", EstablishmentCreateView.as_view(), name='establishment-create'),
    path(
        "establishment/<int:pk>/",
        EstablishmentViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name='establishment-detail'
    ),
    path("menu/<int:pk>/", MenuView.as_view({'get': 'list'}), name='menu-detail'),
    path("establishment/<int:pk>/feedback_list/", FeedbackListView.as_view()),
    path("establishment/<int:pk>/feedback_create/", FeedbackCreateView.as_view()),
]
