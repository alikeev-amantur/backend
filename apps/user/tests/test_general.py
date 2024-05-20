import datetime

import pytest
from django.contrib.auth import get_user_model

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from ..utils import datetime_serializer
from happyhours.factories import (
    UserFactory,
)

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def partner_user():
    return UserFactory(role="partner")


@pytest.fixture
def client_user():
    return UserFactory(role="client")


@pytest.fixture
def admin_user():
    return UserFactory(role="admin")


@pytest.fixture
def access_token_client(client_user):
    token = AccessToken.for_user(client_user)
    return str(token)


@pytest.fixture
def access_token_partner(partner_user):
    token = AccessToken.for_user(partner_user)
    return str(token)


@pytest.fixture
def access_token_admin(admin_user):
    token = AccessToken.for_user(admin_user)
    return str(token)


@pytest.mark.django_db
def test_admin_login_with_access_token(client, access_token_admin):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_admin}')
    url = reverse("v1:partner-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_partner_create(client, access_token_admin):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_admin}')
    url = reverse("v1:create-partner")
    data = {
        "email": "user@example.com",
        "name": "string",
        "password": "stringst",
        "password_confirm": "stringst",
        "max_establishments": 1
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_clients_list(client, access_token_admin):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_admin}')
    url = reverse("v1:client-list")
    response = client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_clients_profile(client, access_token_client):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_client}')
    url = reverse("v1:user-profile")
    response = client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_partners_profile_admin(client, access_token_admin, django_user_model):
    email = "partner@example.com"
    password = "somepassword1"
    role = "partner"
    user = django_user_model.objects.create_user(
        email=email, password=password, role=role
    )
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_admin}')
    url = reverse("v1:partners-profile-admin", args=[user.id])
    response = client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_clients_profile_admin(client, access_token_admin, django_user_model):
    email = "client@example.com"
    password = "somepassword1"
    role = "client"
    user = django_user_model.objects.create_user(
        email=email, password=password, role=role
    )
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token_admin}')
    url = reverse("v1:clients-profile-admin", args=[user.id])
    response = client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_client_login(client, django_user_model):
    url = reverse("v1:token-obtain-pair")
    email = "user@example.com"
    password = "somepassword1"
    role = "client"
    user = django_user_model.objects.create_user(
        email=email, password=password, role=role
    )
    data = {
        "email": email,
        "password": password,
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_client_register(client):
    url = reverse("v1:client-register")
    data = {
        "email": "client@example.com",
        "password": "stringst",
        "password_confirm": "stringst",
        "name": "Client",
        "date_of_birth": "2024-05-20",
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_admin_login(client, django_user_model):
    url = reverse("v1:login-admin")
    email = "amin@example.com"
    password = "adminpassword1"
    role = "admin"
    user = django_user_model.objects.create_user(
        email=email, password=password, role=role
    )
    data = {
        "email": email,
        "password": password,
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_blocked_user(client, django_user_model):
    email = "user@example.com"
    password = "somepassword1"
    role = "client"
    is_blocked = True
    user = django_user_model.objects.create_user(
        email=email, password=password, role=role, is_blocked=is_blocked
    )
    url = reverse("v1:token-obtain-pair")
    data = {
        "email": email,
        "password": password,
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_forgot_page(client):
    url = reverse("v1:password-forgot-page")
    data = {
        "email": "email",
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_reset_code(client):
    session = client.session
    session["reset_code"] = "9267"
    session["reset_code_create_time"] = datetime_serializer(datetime.datetime.now())
    session.save()
    url = reverse("v1:password-reset")
    data = {
        "email": "email@example.com",
        "reset_code": "9263",
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST