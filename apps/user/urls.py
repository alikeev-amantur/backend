from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)

from .views import (
    UserViewSet,
    ClientRegisterView,
    CreatePartner,
    ClientListView,
    TokenObtainView,
    ClientPasswordForgotPageView,
    ClientPasswordResetView,
    ClientPasswordChangeView,
    AdminLoginView,
    PartnerListView,
    BlockUserView,
    PartnerViewSetAdmin,
)

TokenBlacklistView = extend_schema(tags=["Users"])(TokenBlacklistView)
TokenRefreshView = extend_schema(tags=["Users"])(TokenRefreshView)

urlpatterns = [
    path("users/token/", TokenObtainView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/logout/", TokenBlacklistView.as_view(), name="logout"),
    path(
        "users/profile/",
        UserViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="user-profile",
    ),
    path("admins/token/", AdminLoginView.as_view(), name="admin_login"),
    path("admins/users/block/", BlockUserView.as_view(),
         name="block-user"),
    path(
        "admins/partners/<int:pk>/",
        PartnerViewSetAdmin.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="user-profile-admin",
    ),
    path("admins/partners/list/", PartnerListView.as_view(), name="partner-list"),
    path("admins/partners/create/", CreatePartner.as_view(), name="create-partner"),
    path("admins/clients/list/", ClientListView.as_view(), name="client-list"),
    path("clients/register/", ClientRegisterView.as_view(), name="client-register"),
    path(
        "clients/password/forgot/",
        ClientPasswordForgotPageView.as_view(),
        name="password-forgot-page",
    ),
    path("clients/password/reset/", ClientPasswordResetView.as_view(), name="password-reset"),
    path(
        "clients/password/change/", ClientPasswordChangeView.as_view(), name="password-change"
    ),
]
