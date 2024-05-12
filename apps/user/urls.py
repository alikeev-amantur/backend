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
    UserViewSetAdmin,
)

TokenBlacklistView = extend_schema(tags=["Users"])(TokenBlacklistView)
TokenRefreshView = extend_schema(tags=["Users"])(TokenRefreshView)

urlpatterns = [
    path("token/", TokenObtainView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("admin/token/", AdminLoginView.as_view(), name="admin_login"),
    path(
        "admin/profiles/<int:pk>/",
        UserViewSetAdmin.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="user-profile-admin",
    ),
    path("admin/block_user/", BlockUserView.as_view(), name="block-user"),
    path("partners/list", PartnerListView.as_view(), name="partner-list"),
    path("partners/create/", CreatePartner.as_view(), name="create-partner"),
    path("clients/register/", ClientRegisterView.as_view(), name="client-register"),
    path("clients/list/", ClientListView.as_view(), name="client-list"),
    path(
        "clients/profile/",
        UserViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="user-profile",
    ),
    path(
        "clients/password_forgot/",
        ClientPasswordForgotPageView.as_view(),
        name="password-forgot-page",
    ),
    path("cleints/password_reset/", ClientPasswordResetView.as_view(), name="password-reset"),
    path(
        "clients/password_change/", ClientPasswordChangeView.as_view(), name="password-change"
    ),
]
