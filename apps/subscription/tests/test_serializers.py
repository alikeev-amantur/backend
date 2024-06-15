from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from ..serializers import FreeTrialSerializer, SubscriptionPlanSerializer, SubscriptionSerializer
from happyhours.factories import UserFactory, SubscriptionPlanFactory, SubscriptionFactory


@pytest.mark.django_db
def test_free_trial_serializer_valid_plan():
    user = UserFactory()
    plan = SubscriptionPlanFactory(duration='FT', free_trial_days=14)
    data = {'plan_id': plan.id}

    request = APIRequestFactory().post('/free-trial/', data)
    request.user = user

    serializer = FreeTrialSerializer(data=data, context={'request': request})
    assert serializer.is_valid()

    subscription = serializer.save()
    assert subscription.user == user
    assert subscription.plan == plan
    assert subscription.is_trial
    assert subscription.start_date is not None
    assert subscription.end_date


@pytest.mark.django_db
def test_free_trial_serializer_invalid_plan():
    user = UserFactory()
    data = {'plan_id': 999}  # Non-existing plan ID

    request = APIRequestFactory().post('/free-trial/', data)
    request.user = user

    serializer = FreeTrialSerializer(data=data, context={'request': request})
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)

    assert 'Subscription plan does not exist.' in str(excinfo.value)


@pytest.mark.django_db
def test_subscription_plan_serializer_valid():
    data = {
        'name': 'Test Plan',
        'duration': '1M',
        'price': '9.99',
        'description': 'Test description',
        'free_trial_days': 0
    }

    serializer = SubscriptionPlanSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    plan = serializer.save()
    assert plan.name == data['name']
    assert plan.duration == data['duration']
    assert plan.price == Decimal(data['price'])
    assert plan.description == data['description']
    assert plan.free_trial_days == data['free_trial_days']


@pytest.mark.django_db
def test_subscription_plan_serializer_invalid_free_trial():
    data = {
        'name': 'Test Plan',
        'duration': '1M',
        'price': '0',
        'description': 'Test description',
        'free_trial_days': 14
    }

    serializer = SubscriptionPlanSerializer(data=data)
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)

    assert 'Duration must be FT for free trial days' in str(excinfo.value)


@pytest.mark.django_db
def test_subscription_plan_serializer_invalid_price_for_trial():
    data = {
        'name': 'Test Plan',
        'duration': 'FT',
        'price': '9.99',
        'description': 'Test description',
        'free_trial_days': 14
    }

    serializer = SubscriptionPlanSerializer(data=data)
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)

    assert 'Price must be zero for free trial plans.' in str(excinfo.value)


@pytest.mark.django_db
def test_subscription_serializer():
    user = UserFactory()
    plan = SubscriptionPlanFactory()
    subscription = SubscriptionFactory(user=user, plan=plan)

    serializer = SubscriptionSerializer(subscription)
    data = serializer.data

    assert data['id'] == subscription.id
    assert data['user'] == user.id
    assert data['plan']['id'] == plan.id
    assert data['start_date'] == timezone.localtime(subscription.start_date).isoformat()
    assert data['end_date'] == timezone.localtime(subscription.end_date).isoformat()
    assert data['is_active'] == subscription.is_active
    assert data['is_trial'] == subscription.is_trial
