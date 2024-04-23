from django.contrib.auth import get_user_model
from rest_framework.generics import (
    RetrieveAPIView, UpdateAPIView, DestroyAPIView, CreateAPIView
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import ViewSetMixin
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    UserSerializer, TokenObtainSerializer, ClientRegisterSerializer,
    PartnerCreateSerializer
)
from happyhours.permissions import IsUserOwner

User = get_user_model()


class TokenObtainView(TokenObtainPairView):
    serializer_class = TokenObtainSerializer


class ClientRegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ClientRegisterSerializer


class UserViewSet(ViewSetMixin,
                  RetrieveAPIView,
                  UpdateAPIView,
                  DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserOwner]


class CreatePartner(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = PartnerCreateSerializer
    permission_classes = [IsAdminUser]

