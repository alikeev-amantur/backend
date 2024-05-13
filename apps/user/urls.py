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
    PartnerViewSetAdmin, ClientExistenceView,
)

TokenBlacklistView = extend_schema(tags=["Users"])(TokenBlacklistView)
TokenRefreshView = extend_schema(tags=["Users"])(TokenRefreshView)

urlpatterns = [
    path("auth/token/", TokenObtainView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),
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
    path("admin/auth/token/", AdminLoginView.as_view(), name="admin_login"),
    path("admin/users/block/", BlockUserView.as_view(),
         name="block-user"),
    path(
        "admin/partners/<int:pk>/",
        PartnerViewSetAdmin.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="user-profile-admin",
    ),
    path("admin/partners/list/", PartnerListView.as_view(), name="partner-list"),
    path("admin/partners/create/", CreatePartner.as_view(), name="create-partner"),
    path("admin/clients/list/", ClientListView.as_view(), name="client-list"),
    path("partner/clients/existence/", ClientExistenceView.as_view(), name="client-existence"),
    path("client/register/", ClientRegisterView.as_view(), name="client-register"),
    path(
        "client/password/forgot/",
        ClientPasswordForgotPageView.as_view(),
        name="password-forgot-page",
    ),
    path("client/password/reset/", ClientPasswordResetView.as_view(), name="password-reset"),
    path(
        "client/password/change/", ClientPasswordChangeView.as_view(), name="password-change"
    ),
]
