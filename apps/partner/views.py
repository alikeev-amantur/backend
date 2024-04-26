from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSetMixin

from .models import Establishment, QRCode
from .serializers import (
    EstablishmentSerializer,
    EstablishmentCreateUpdateSerializer,
    MenuSerializer,
)
from .utils import generate_qr_code
from happyhours.permissions import (
    IsAdmin,
    IsPartnerOwner, IsPartnerUser,
)


@extend_schema(tags=['Establishments'])
class EstablishmentListView(ListAPIView):
    """
    List all establishments.
    For partners, only list their own establishments.
    """
    serializer_class = EstablishmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'partner':
            return Establishment.objects.filter(owner=user)
        return Establishment.objects.all()


@extend_schema(tags=['Establishments'])
class EstablishmentCreateView(CreateAPIView):
    """
    Establishment create view (should be only for admin)
    Contains validation for phone_number and location fields
    Permissions only for admin
    """

    queryset = Establishment.objects.all()
    serializer_class = EstablishmentCreateUpdateSerializer

    permission_classes = [IsPartnerUser]

    def perform_create(self, serializer):
        user = self.request.user
        if user.max_establishments <= Establishment.objects.filter(owner=user).count():
            raise PermissionDenied('This partner has reached their maximum number of establishments.')
        establishment = serializer.save()
        domain = self.request.build_absolute_uri("/")
        filename, qr_code_data = generate_qr_code(establishment, domain)
        qr_code = QRCode(establishment=establishment)
        qr_code.qr_code_image.save(filename, ContentFile(qr_code_data), save=False)
        qr_code.save()


@extend_schema(tags=['Establishments'])
class EstablishmentViewSet(
    ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView
):
    """
    Establishment view set:
    Retrieve - for all users
    Update - only for establishment partner (owner) or admin
    Delete - only for admin
    Contains validation for phone_number and location fields
    Permission for each user group.
    """

    queryset = Establishment.objects.all()

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return EstablishmentCreateUpdateSerializer
        return EstablishmentSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permissions = [IsAuthenticated]
        elif self.action in ('update', 'partial_update'):
            permissions = [IsPartnerOwner]
        else:
            permissions = [IsAdmin]
        return [permission() for permission in permissions]


@extend_schema(tags=['Establishments'])
class MenuView(RetrieveAPIView):
    """Establishment's menu"""

    queryset = Establishment.objects.all()
    serializer_class = MenuSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
