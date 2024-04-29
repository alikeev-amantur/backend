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
    ClientPasswordChangeView
)

TokenBlacklistView = extend_schema(tags=["Users"])(TokenBlacklistView)
TokenRefreshView = extend_schema(tags=["Users"])(TokenRefreshView)


urlpatterns = [
    path("token/", TokenObtainView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("client_register/", ClientRegisterView.as_view(), name="client-register"),
    path("client_list/", ClientListView.as_view(), name="client-list"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("create_partner/", CreatePartner.as_view(), name="create-partner"),
    path(
        "<int:pk>/",
        UserViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        'password_forgot/', ClientPasswordForgotPageView.as_view(),
        name='password-forgot-page'
    ),
    path(
        'password_reset/', ClientPasswordResetView.as_view(),
        name='password-reset'
    ),
    path(
        'password_change/', ClientPasswordChangeView.as_view(),
        name='password-change'
    ),
]
