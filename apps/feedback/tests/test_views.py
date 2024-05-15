import pytest
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from happyhours.factories import (
    UserFactory,
    EstablishmentFactory,
    FeedbackFactory,
)


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def partner_user():
    return UserFactory(role="partner")


@pytest.fixture
def normal_user():
    return UserFactory(role="client")


@pytest.fixture
def partner_establishment(partner_user):
    return EstablishmentFactory(owner=partner_user)


@pytest.fixture
def feedback(normal_user):
    return FeedbackFactory(user=normal_user)


@pytest.mark.django_db
def test_retrieve_feedback(client, normal_user, feedback):
    client.force_authenticate(user=normal_user)
    url = reverse("v1:feedback-viewset", args=[feedback.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_feedback(client, normal_user, partner_establishment):
    client.force_authenticate(user=normal_user)
    url = reverse("v1:feedback-create")
    data = {
        "establishment": partner_establishment.id,
        "text": "string"
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_feedback_answer(client, normal_user, feedback):
    client.force_authenticate(user=normal_user)
    url = reverse("v1:feedback-answer-create")
    data = {
        "feedback": feedback.id,
        "text": "string"
    }
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
