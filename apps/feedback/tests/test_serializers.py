import pytest

from django.contrib.auth import get_user_model
from django.test import RequestFactory

from happyhours.factories import (
    FeedbackFactory,
    FeedbackAnswerFactory,
    EstablishmentFactory,
    UserFactory,
)
from ..serializers import (
    FeedbackSerializer,
    FeedbackAnswerSerializer,
)

User = get_user_model()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def another_user():
    return UserFactory()


@pytest.fixture
def mock_request(user):
    request = RequestFactory().get("/fake-url")
    request.user = user
    return request


@pytest.fixture
def establishment(user):
    return EstablishmentFactory(owner=user)


@pytest.fixture
def feedback(user):
    return FeedbackFactory(user=user)


@pytest.fixture
def feedback_answer(user):
    return FeedbackAnswerFactory(user=user)


@pytest.mark.django_db
def test_validate_feedback(feedback, mock_request):
    serializer = FeedbackSerializer(context={"request": mock_request})
    assert serializer.validate(feedback) == feedback


@pytest.mark.django_db
def test_validate_feedback_answer(feedback_answer, mock_request):
    serializer = FeedbackAnswerSerializer(context={"request": mock_request})
    assert serializer.validate(feedback_answer) == feedback_answer
