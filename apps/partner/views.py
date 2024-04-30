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
from happyhours.permissions import (
    IsAdmin,
    IsPartnerOwner,
    IsPartnerUser,
)
from .serializers import (
    EstablishmentSerializer,
    EstablishmentCreateUpdateSerializer,
    MenuSerializer,
)
from .utils import generate_qr_code
from .models import Establishment, QRCode

@extend_schema(tags=["Establishments"])
class EstablishmentListView(ListAPIView):
    """
    Lists establishments based on user roles. This view is accessible to all
    authenticated users. Partners see only
    establishments they own.

    ### Access Control:
    - All authenticated users can access this view, but the listings are
    filtered by ownership for partners,
      showing only their own establishments.
    - Admins have the privilege to view all establishments across the platform

    ### Implementation Details:
    - The queryset dynamically adjusts based on the authenticated user's role,
    ensuring that users receive data
      that is relevant and appropriate to their permissions.
    """

    serializer_class = EstablishmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "partner":
            return Establishment.objects.filter(owner=user)
        return Establishment.objects.all()


@extend_schema(tags=["Establishments"])
class EstablishmentCreateView(CreateAPIView):
    """
    Creates a new establishment, restricted to partner users who can
     create up to their allowed limit.
    This view also handles the generation of a QR code for each new establishment,
     which is saved and linked
    to the establishment for easy access and identification.

    ### Fields:
    - `name`: The name of the establishment.
    - `location`: The geographic location of the establishment.
    - `description`: A brief description of the establishment.
    - `phone_number`: The contact phone number for the establishment.
    - `logo`: A URL to the logo image for the establishment.
    - `address`: The full address of the establishment.
    - `happyhours_start`: The start time for happy hours.
    - `happyhours_end`: The end time for happy hours.
    - `owner`: The id of the partner user.
    - `qr_code`: A URL to the QR code image for the establishment (read-only).

    ### Validation:
    - Ensures that the partner has not exceeded their limit of owned establishments.
    - Checks data integrity for phone numbers and locations.

    ### Permission:
    - Restricted to authenticated partner users only.

    ### Business Logic:
    - On successful creation, a QR code is generated and saved associated
    with the establishment.
    - The creation will fail with a `Permission Denied` error
    if the user has reached their limit of establishments.

    """

    queryset = Establishment.objects.all()
    serializer_class = EstablishmentCreateUpdateSerializer

    permission_classes = [IsPartnerUser]

    def perform_create(self, serializer):
        user = self.request.user
        if user.max_establishments <= Establishment.objects.filter(owner=user).count():
            raise PermissionDenied(
                "This partner has reached their maximum number of establishments."
            )
        establishment = serializer.save()
        domain = self.request.build_absolute_uri("/")
        filename, qr_code_data = generate_qr_code(establishment, domain)
        qr_code = QRCode(establishment=establishment)
        qr_code.qr_code_image.save(filename, ContentFile(qr_code_data), save=False)
        qr_code.save()


@extend_schema(tags=["Establishments"])
class EstablishmentViewSet(
    ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView
):
    """
    Manages the CRUD operations for establishments. Retrieve is open to all users,
    update and delete are
    restricted to admins and owners, ensuring operational security and owner control.
    """

    queryset = Establishment.objects.all()

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return EstablishmentCreateUpdateSerializer
        return EstablishmentSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            permissions = [IsAuthenticated]
        elif self.action in ("update", "partial_update"):
            permissions = [IsPartnerOwner]
        else:
            permissions = [IsAdmin]
        return [permission() for permission in permissions]


@extend_schema(tags=["Establishments"])
class MenuView(RetrieveAPIView):
    """Provides a detailed view of the menu for a specific establishment,
    accessible to all authenticated users."""

    queryset = Establishment.objects.all()
    serializer_class = MenuSerializer
    # lookup_field = "id"
    permission_classes = [IsAuthenticated]
