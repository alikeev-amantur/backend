from django.contrib.auth import get_user_model

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin
from rest_framework_simplejwt.tokens import RefreshToken
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token),
                          "access": str(token.access_token)}
        headers = self.get_success_headers(serializer.data)
        return Response(
            data, status=status.HTTP_201_CREATED, headers=headers
        )


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
