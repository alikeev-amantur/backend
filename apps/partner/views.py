from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ViewSetMixin

from .models import Establishment
from .serializers import EstablishmentSerializer


class EstablishmentPagination(PageNumberPagination):
    """
    Pagination for establishment
    """
    page_size = 7


class EstablishmentListView(ListAPIView):
    """
    List all establishments. Ordered by id
    """
    queryset = Establishment.objects.all().order_by('id')
    serializer_class = EstablishmentSerializer
    pagination_class = EstablishmentPagination


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
