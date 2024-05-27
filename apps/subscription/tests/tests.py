import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from happyhours.factories import UserFactory, SubscriptionPlanFactory, SubscriptionFactory



@pytest.mark.django_db
def test_cancel_payment_view():
    user = UserFactory()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse('v1:cancel-payment'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'Payment cancelled'


@pytest.mark.django_db
def test_free_trial_view():
    user = UserFactory()
    plan = SubscriptionPlanFactory(duration='FT', free_trial_days=14)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(reverse('v1:free-trial'), {'plan_id': plan.id})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'Free trial activated'
    assert 'subscription_id' in response.data


@pytest.mark.django_db
def test_subscription_plan_viewset():
    user = UserFactory()
    plan = SubscriptionPlanFactory()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse('v1:subscriptionplan-list'))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


@pytest.mark.django_db
def test_user_subscriptions_view():
    user = UserFactory()
    plan = SubscriptionPlanFactory()
    subscription = SubscriptionFactory(user=user, plan=plan)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse('v1:user-subscriptions', kwargs={'user_id': user.id}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


@pytest.mark.django_db
def test_deactivate_subscription_view():
    user = UserFactory()
    plan = SubscriptionPlanFactory()
    subscription = SubscriptionFactory(user=user, plan=plan, is_active=True)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(reverse('v1:deactivate-subscription', kwargs={'pk': subscription.id}))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Subscription deactivated successfully.'

    subscription.refresh_from_db()
    assert not subscription.is_active
