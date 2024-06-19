import pytest
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from happyhours.factories import (
    UserFactory,
    EstablishmentFactory,
    FeedbackFactory, FeedbackAnswerFactory,
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
def test_create_feedback(client, partner_establishment):
    user = UserFactory(role='client')
    client.force_authenticate(user=user)
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

@pytest.mark.django_db
def test_feedback_list_view():
    client = APIClient()

    establishment = EstablishmentFactory()
    feedback1 = FeedbackFactory(establishment=establishment)
    feedback2 = FeedbackFactory(establishment=establishment)

    url = reverse('v1:feedback-list', kwargs={'establishment_id': establishment.id})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['id'] == feedback1.id
    assert response.data[1]['id'] == feedback2.id

@pytest.mark.django_db
def test_feedback_list_view_invalid_establishment():
    client = APIClient()

    invalid_establishment_id = 9999
    url = reverse('v1:feedback-list', kwargs={'establishment_id': invalid_establishment_id})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0

@pytest.mark.django_db
def test_feedback_answer_list_view():
    client = APIClient()

    feedback = FeedbackFactory()
    feedback_answer1 = FeedbackAnswerFactory(feedback=feedback)
    feedback_answer2 = FeedbackAnswerFactory(feedback=feedback)

    url = reverse('v1:feedback-answer-list', kwargs={'pk': feedback.id})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['id'] == feedback_answer1.id
    assert response.data[1]['id'] == feedback_answer2.id

@pytest.mark.django_db
def test_feedback_answer_list_view_invalid_feedback():
    client = APIClient()

    invalid_feedback_id = 9999
    url = reverse('v1:feedback-answer-list', kwargs={'pk': invalid_feedback_id})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0