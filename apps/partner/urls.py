from django.urls import path

from .views import (
    EstablishmentListView, EstablishmentCreateView, EstablishmentViewSet
)

urlpatterns = [
    path('establishment/list/', EstablishmentListView.as_view()),
    path('establishment/create/', EstablishmentCreateView.as_view()),
    path('establishment/<int:pk>/', EstablishmentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    })),
]
