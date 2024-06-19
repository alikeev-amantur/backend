from unittest.mock import patch, MagicMock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from apps.subscription.models import Subscription
from apps.subscription.views import ExecutePaymentView
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


@pytest.mark.django_db
def test_active_user_subscription_view():
    user = UserFactory()
    plan = SubscriptionPlanFactory()

    inactive_subscription = SubscriptionFactory(user=user, plan=plan, is_active=False)
    active_subscription = SubscriptionFactory(user=user, plan=plan, is_active=True)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse('v1:active-subscription')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    assert response.data['id'] == active_subscription.id
    assert response.data['is_active'] is True


@pytest.mark.django_db
def test_subscription_statistics_view():
    admin_user = UserFactory(role='admin')
    normal_user = UserFactory(role='client')

    plan1 = SubscriptionPlanFactory(name="Plan 1", price=100)
    plan2 = SubscriptionPlanFactory(name="Plan 2", price=200)

    SubscriptionFactory(user=normal_user, plan=plan1, is_active=True, is_trial=False)
    SubscriptionFactory(user=normal_user, plan=plan2, is_active=False, is_trial=True)
    SubscriptionFactory(user=normal_user, plan=plan1, is_active=True, is_trial=False)

    client = APIClient()
    client.force_authenticate(user=admin_user)

    url = reverse('v1:subscription-statistics')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['all_subscriptions'] == 3
    assert response.data['active_subscriptions'] == 2
    assert response.data['inactive_subscriptions'] == 1
    assert response.data['trial_subscriptions'] == 1
    assert response.data['total_price'] == 400
    assert len(response.data['most_popular_plans']) == 2
    assert response.data['most_popular_plans'][0]['plan__name'] == "Plan 1"
    assert response.data['most_popular_plans'][0]['count'] == 2


@pytest.mark.django_db
def test_subscription_statistics_view_permission_denied():
    normal_user = UserFactory(role='client')

    client = APIClient()
    client.force_authenticate(user=normal_user)

    url = reverse('v1:subscription-statistics')
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@patch('apps.subscription.views.paypalrestsdk.Payment')
def test_create_payment_view(mock_payment_class):
    user = UserFactory()
    plan = SubscriptionPlanFactory(price=50.00)
    SubscriptionFactory(user=user, plan=plan, is_active=False, is_trial=False)

    access_token = str(AccessToken.for_user(user))

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    mock_payment = MagicMock()
    mock_payment.create.return_value = True
    mock_payment.links = [MagicMock(rel="approval_url", href="http://approval.url")]

    mock_payment_class.return_value = mock_payment

    url = reverse('v1:create-payment', kwargs={'plan_id': plan.id})
    response = client.post(url)

    # Debugging logs
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Data: {response.data}")

    assert response.status_code == status.HTTP_200_OK, f"Expected 200 but got {response.status_code} - {response.data}"
    assert 'approval_url' in response.data, f"Expected 'approval_url' in response but got {response.data}"
    assert response.data['approval_url'] == "http://approval.url"


@pytest.mark.django_db
@patch('apps.subscription.views.paypalrestsdk.Payment')
def test_create_payment_view_already_subscribed(mock_payment_class):
    user = UserFactory()
    plan = SubscriptionPlanFactory(price=50.00)
    SubscriptionFactory(user=user, plan=plan, is_active=True, is_trial=False)

    access_token = str(AccessToken.for_user(user))

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    url = reverse('v1:create-payment', kwargs={'plan_id': plan.id})
    response = client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400 but got {response.status_code} - {response.data}"
    assert 'error' in response.data, f"Expected 'error' in response but got {response.data}"
    assert response.data['error'] == 'You already have an active subscription for this plan.'


@pytest.mark.django_db
@patch('apps.subscription.views.paypalrestsdk.Payment')
def test_create_payment_view_payment_error(mock_payment_class):
    user = UserFactory()
    plan = SubscriptionPlanFactory(price=50.00)
    access_token = str(AccessToken.for_user(user))

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    mock_payment = MagicMock()
    mock_payment.create.return_value = False
    mock_payment.error = {'message': 'Error message'}

    mock_payment_class.return_value = mock_payment

    url = reverse('v1:create-payment', kwargs={'plan_id': plan.id})
    response = client.post(url)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, f"Expected 500 but got {response.status_code} - {response.data}"
    assert 'error' in response.data, f"Expected 'error' in response but got {response.data}"
    assert response.data['error'] == {'message': 'Error message'}


@pytest.mark.django_db
@patch('apps.subscription.views.paypalrestsdk.Payment')
@patch.object(ExecutePaymentView, 'authenticate_token')
def test_execute_payment_view(mock_authenticate_token, mock_payment_class):
    user = UserFactory()
    plan = SubscriptionPlanFactory(price=50.00)

    access_token = str(AccessToken.for_user(user))

    client = APIClient()

    mock_payment = MagicMock()
    mock_payment.execute.return_value = True
    mock_payment.transactions = [
        MagicMock(item_list=MagicMock(items=[MagicMock(sku=plan.id)]))
    ]
    mock_payment_class.find.return_value = mock_payment

    mock_authenticate_token.return_value = user

    url = reverse('v1:execute-payment')
    response = client.get(url, {
        'paymentId': 'PAYID-12345',
        'PayerID': 'PAYERID-67890',
        'access_token': access_token
    })

    assert response.status_code == status.HTTP_200_OK, f"Expected 200 but got {response.status_code} - {response.data}"
    assert response.data['status'] == 'Payment executed successfully'
    assert Subscription.objects.filter(user=user, plan=plan).exists()


@pytest.mark.django_db
@patch('apps.subscription.views.paypalrestsdk.Payment')
@patch.object(ExecutePaymentView, 'authenticate_token')
def test_execute_payment_view_invalid_token(mock_authenticate_token, mock_payment_class):
    user = UserFactory()
    plan = SubscriptionPlanFactory(price=50.00)

    access_token = 'invalidtoken'

    client = APIClient()

    mock_authenticate_token.return_value = None

    url = reverse('v1:execute-payment')
    response = client.get(url, {
        'paymentId': 'PAYID-12345',
        'PayerID': 'PAYERID-67890',
        'access_token': access_token
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Expected 401 but got {response.status_code} - {response.data}"
    assert response.data['error'] == 'Invalid access token'


@pytest.mark.django_db
@patch('apps.subscription.views.paypalrestsdk.Payment')
@patch.object(ExecutePaymentView, 'authenticate_token')
def test_execute_payment_view_payment_error(mock_authenticate_token, mock_payment_class):
    user = UserFactory()
    plan = SubscriptionPlanFactory(price=50.00)

    access_token = str(AccessToken.for_user(user))

    client = APIClient()

    mock_payment = MagicMock()
    mock_payment.execute.return_value = False
    mock_payment.error = {'message': 'Error executing payment'}
    mock_payment_class.find.return_value = mock_payment

    mock_authenticate_token.return_value = user

    url = reverse('v1:execute-payment')
    response = client.get(url, {
        'paymentId': 'PAYID-12345',
        'PayerID': 'PAYERID-67890',
        'access_token': access_token
    })

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, f"Expected 500 but got {response.status_code} - {response.data}"
    assert response.data['error'] == {'message': 'Error executing payment'}
