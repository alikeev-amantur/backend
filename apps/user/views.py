import datetime

from django.contrib.auth import get_user_model

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
    ListAPIView,
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from happyhours.permissions import (
    IsUserOwner,
    IsPartnerAndAdmin,
    IsNotAuthenticated,
    IsAdmin,
)

from .serializers import (
    UserSerializer,
    TokenObtainSerializer,
    ClientRegisterSerializer,
    PartnerCreateSerializer,
    ClientPasswordForgotPageSerializer,
    ClientPasswordResetSerializer,
    ClientPasswordChangeSerializer,
    AdminLoginSerializer
)
from .utils import (
    generate_reset_code,
    datetime_serializer,
    datetime_deserializer,
    send_reset_code_email
)

User = get_user_model()


@extend_schema(tags=["Users"])
class TokenObtainView(TokenObtainPairView):
    """
    Token Obtaining view
    """

    serializer_class = TokenObtainSerializer


@extend_schema(tags=["Users"])
class AdminLoginView(TokenObtainView):
    """
    Individual login for Admin and superuser
    """
    serializer_class = AdminLoginSerializer


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
class ClientPasswordChangeView(GenericAPIView):
    serializer_class = ClientPasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response(
            'Password successfully changed', status=status.HTTP_200_OK
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
    permission_classes = [IsAdmin]


@extend_schema(tags=["Users"])
class ClientListView(ListAPIView):
    queryset = User.objects.all().filter(role="client").order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsPartnerAndAdmin]


@extend_schema(tags=["Users"])
class ClientPasswordForgotPageView(GenericAPIView):
    serializer_class = ClientPasswordForgotPageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_code = generate_reset_code()
        user = serializer.validated_data['email']
        request.session['reset_code'] = str(reset_code)
        time_now = datetime.datetime.now()
        request.session['reset_code_create_time'] = (
            datetime_serializer(time_now))
        send_reset_code_email(user, reset_code)
        return Response('Success', status=status.HTTP_200_OK)


@extend_schema(tags=["Users"])
class ClientPasswordResetView(GenericAPIView):
    serializer_class = ClientPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_code = serializer.validated_data['reset_code']

        if ('reset_code' in request.session
                and 'reset_code_create_time' in request.session):
            stored_code = request.session['reset_code']
            stored_code_date = datetime_deserializer(
                request.session['reset_code_create_time']
            )
            passed_time = datetime.datetime.now()

            if (stored_code == reset_code and
                    (passed_time - stored_code_date).total_seconds() < 600):
                user = User.objects.get(
                    email=serializer.validated_data['email']
                )
                token = RefreshToken.for_user(user)
                request.session['reset_code'] = ''
                request.session['reset_code_create_time'] = ''
                return Response(
                    {'refresh': str(token), 'access': str(token.access_token)}
                )
        return Response('Invalid code', status=status.HTTP_400_BAD_REQUEST)
