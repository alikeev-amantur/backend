from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
)
from rest_framework.viewsets import ViewSetMixin

from .models import Establishment
from .serializers import EstablishmentSerializer


class EstablishmentListView(ListAPIView):
    """
    List all establishments
    TODO: add pagination
    """
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer


class EstablishmentCreateView(CreateAPIView):
    """
    Establishment create view (should be only for admin)
    TODO: add permissions only for admin, add validation
    """
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer


class EstablishmentViewSet(ViewSetMixin,
                           RetrieveAPIView,
                           UpdateAPIView,
                           DestroyAPIView):
    """
    Establishment view set:
    Retrieve - for all users
    Update - only for establishment partner (owner) or admin
    Delete - only for admin
    TODO: implement permission for each user group. Add validation for update
    """
    queryset = Establishment.objects.all()
    serializer_class = EstablishmentSerializer
