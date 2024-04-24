from django.core.files.base import ContentFile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ViewSetMixin

from .filters import EstablishmentFilter
from .models import Establishment, QRCode
from .serializers import (
    EstablishmentSerializer,
    EstablishmentCreateUpdateSerializer,
    MenuSerializer,
)
from .utils import generate_qr_code


class EstablishmentPagination(PageNumberPagination):
    """
    Pagination for establishment
    """

    page_size = 10


class EstablishmentListView(ListAPIView):
    """
    List all establishments. Ordered by id
    """

    queryset = Establishment.objects.all().order_by("id")
    serializer_class = EstablishmentSerializer
    pagination_class = EstablishmentPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = EstablishmentFilter


class EstablishmentCreateView(CreateAPIView):
    """
    Establishment create view (should be only for admin)
    Contains validation for phone_number and location fields
    TODO: add permissions only for admin
    """

    queryset = Establishment.objects.all()
    serializer_class = EstablishmentCreateUpdateSerializer

    def perform_create(self, serializer):
        establishment = serializer.save()
        domain = self.request.build_absolute_uri("/")[:-1]
        filename, qr_code_data = generate_qr_code(establishment, domain)
        qr_code = QRCode(establishment=establishment)
        qr_code.qr_code_image.save(filename, ContentFile(qr_code_data), save=False)
        qr_code.save()


class EstablishmentViewSet(
    ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView
):
    """
    Establishment view set:
    Retrieve - for all users
    Update - only for establishment partner (owner) or admin
    Delete - only for admin
    Contains validation for phone_number and location fields
    TODO: implement permission for each user group.
    """

    queryset = Establishment.objects.all()

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return EstablishmentCreateUpdateSerializer
        return EstablishmentSerializer


class MenuView(RetrieveAPIView):
    """accessing menu via qr code"""

    queryset = Establishment.objects.all()
    serializer_class = MenuSerializer
    lookup_field = "id"
