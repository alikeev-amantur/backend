from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ViewSetMixin
from rest_framework_simplejwt.views import TokenObtainPairView

from happyhours.permissions import IsUserOwner, IsPartnerAndAdmin, IsNotAuthenticated

from .serializers import (
    UserSerializer,
    TokenObtainSerializer,
    ClientRegisterSerializer,
    PartnerCreateSerializer,
)

User = get_user_model()


@extend_schema(tags=["Users"])
class TokenObtainView(TokenObtainPairView):
    """
    Token Obtaining view
    """

    serializer_class = TokenObtainSerializer


@extend_schema(tags=["Users"])
class ClientRegisterView(CreateAPIView):
    """
    Individual Client Register View
    """

    queryset = User.objects.all()
    permission_classes = [IsNotAuthenticated]
    serializer_class = ClientRegisterSerializer


@extend_schema(tags=["Users"])
class UserViewSet(ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    User viewset with Owner permission
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserOwner]


@extend_schema(tags=["Users"])
class CreatePartner(CreateAPIView):
    """
    Individual Partner Register View
    """

    queryset = User.objects.all()
    serializer_class = PartnerCreateSerializer
    permission_classes = [IsAdminUser]


@extend_schema(tags=["Users"])
class ClientListView(ListAPIView):
    queryset = User.objects.all().filter(role="client").order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsPartnerAndAdmin]
