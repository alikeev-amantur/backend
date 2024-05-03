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
    get_object_or_404,
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
    IsAuthenticatedAndNotAdmin,
)

from .serializers import (
    UserSerializer,
    TokenObtainSerializer,
    ClientRegisterSerializer,
    PartnerCreateSerializer,
    ClientPasswordForgotPageSerializer,
    ClientPasswordResetSerializer,
    ClientPasswordChangeSerializer,
    AdminLoginSerializer,
    ClientListSerializer,
    PartnerListSerializer,
    BlockUserSerializer
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
    User authorization. View responsible for creating valid refresh and access
    tokens. Users of all roles can access this view. But admin have separated
    view. Return not only tokens but a user's information
    (id, email, name, role, max_establishments)

    ### Access Control:
    - All authenticated users can access this view.

    ### Implementation Details:
    - Serializer check if user exists in queryset. If not will throw an
    exception. Additionally, checks if user does not have flag is_blocked. If
    it is blocked, the user won't receive tokens
    """

    serializer_class = TokenObtainSerializer


@extend_schema(tags=["Users"])
class AdminLoginView(TokenObtainView):
    """
    Separated admin authorization. View responsible for creating valid refresh
    and access tokens for admin role or superuser.
    Return not only tokens but a user's information
    (id, email, name, role, max_establishments)

    ### Access Control:
    - Only users with admin role or superuser

    ### Implementation Details:
    - Serializer check if user exists in queryset. If not will throw an
    exception, checks if user has admin role or superuser
    """
    serializer_class = AdminLoginSerializer


@extend_schema(tags=["Users"])
class ClientRegisterView(CreateAPIView):
    """
    Client user creation. View responsible for creating user object with role
    client. Only admin or superuser can access this view.
    Returns tokens and the user's information

    ### Fields:
    - `email`: Email address of the client user
    - `password`: Password of the client user
    - `password_confirm` : Password confirmation
    - `name`: Name of the client user
    - `date_of_birth`: Birth date of client user
    - `avatar`: Profile image of client user [Optional]

    ### Access Control:
    - Only unauthenticated users can access this view

    ### Implementation Details:
    - Obtains tokens in create function

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
        password = (serializer.validated_data.get('password'))
        email = (serializer.validated_data.get('email'))
        data["tokens"] = {"refresh": str(token),
                          "access": str(token.access_token)}
        headers = self.get_success_headers(serializer.data)
        return Response(
            data, status=status.HTTP_201_CREATED, headers=headers
        )


@extend_schema(tags=["Users"])
class ClientPasswordChangeView(GenericAPIView):
    """
    User password change creation. View responsible for changing password of
    users (client, partner). Admin and superuser can not access this view.

    ### Fields:
    - `password`: Password of the user
    - `password_confirm` : Password confirmation

    ### Access Control:
    - Only unauthenticated users (client or partner) can access this view

    ### Implementation Details:
    - Sets new password

    """

    serializer_class = ClientPasswordChangeSerializer
    permission_classes = [IsAuthenticatedAndNotAdmin]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=self.request.user.email)
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response(
            'Password successfully changed', status=status.HTTP_200_OK
        )


@extend_schema(tags=["Users"])
class UserViewSet(ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    User viewset with Owner permission. Does not usr ID, takes user from request
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserOwner]

    def get_object(self):
        """

        :return:
        """
        obj = get_object_or_404(self.queryset, id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


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
    serializer_class = ClientListSerializer
    permission_classes = [IsPartnerAndAdmin]


@extend_schema(tags=["Users"])
class PartnerListView(ListAPIView):
    queryset = User.objects.all().filter(role="partner").order_by("id")
    serializer_class = PartnerListSerializer
    permission_classes = [IsAdmin]


@extend_schema(tags=["Users"])
class BlockUserView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = BlockUserSerializer
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data["email"])
        user.is_blocked = True
        user.save()
        return Response("Successful", status=status.HTTP_200_OK)


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
