import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from apps.order.models import Order
from happyhours.factories import (
    UserFactory,
    BeverageFactory,
    EstablishmentFactory,
    OrderFactory, SubscriptionFactory, CategoryFactory,
)


@pytest.mark.django_db
class TestOrderViews:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory(role="client")
        self.partner = UserFactory(role="partner")
        self.establishment = EstablishmentFactory(
            owner=self.partner, happyhours_start="01:00:00", happyhours_end="23:59:00"
        )
        self.beverage = BeverageFactory(establishment=self.establishment)
        self.order = OrderFactory(client=self.user, beverage=self.beverage)
        self.place_order_url = reverse("v1:place-order")
        self.client_order_history_url = reverse("v1:client-order-history-list")
        establishment_id = self.establishment.id
        self.partner_order_history_url = reverse("v1:partner-order-history",args=[establishment_id])

    def test_place_order_permissions(self):
        response = self.client.post(self.place_order_url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        establishment = EstablishmentFactory(
            happyhours_start="00:00:00", happyhours_end="23:59:00"
        )
        beverage = BeverageFactory(establishment=establishment)
        user = UserFactory(role="client")
        SubscriptionFactory(user=user)
        self.client.force_authenticate(user=user)
        order_data = {"beverage": beverage.id}
        response = self.client.post(self.place_order_url, order_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["client"] == user.id
        assert response.data["establishment"] == beverage.establishment.id

    def test_client_order_history_permissions(self):
        response = self.client.get(self.client_order_history_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.client_order_history_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Order.objects.filter(client=self.user).count()

    def test_partner_order_history_permissions(self):
        response = self.client.get(self.partner_order_history_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_authenticate(user=self.partner)
        response = self.client.get(self.partner_order_history_url)
        assert response.status_code == status.HTTP_200_OK

    def test_partner_order_history_data(self):
        self.client.force_authenticate(user=self.partner)
        response = self.client.get(self.partner_order_history_url)
        assert (
                len(response.data)
                == Order.objects.filter(establishment__owner=self.partner).count()
        )


@pytest.mark.django_db
class TestPartnerPlaceOrderView:
    def setup_method(self):
        self.client = APIClient()
        self.partner = UserFactory(role="partner")
        self.client_user = UserFactory(role="client", email='nine@mail.com')
        self.establishment = EstablishmentFactory(owner=self.partner, happyhours_start='00:00:00',
                                                  happyhours_end='23:59:00')
        self.beverage = BeverageFactory(establishment=self.establishment)
        self.url = reverse("v1:partner-place-order")

    def test_place_order_permissions(self):
        response = self.client.post(self.url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        self.client.force_authenticate(user=self.partner)
        response = self.client.post(self.url, {})
        assert response.status_code not in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_partner_place_order(self):
        self.client.force_authenticate(user=self.partner)
        SubscriptionFactory(user=self.client_user)
        data = {
            'client_email': self.client_user.email,
            'beverage': self.beverage.id
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['client'] == self.client_user.id
        assert response.data['establishment'] == self.establishment.id

    def test_invalid_beverage(self):
        self.client.force_authenticate(user=self.partner)
        data = {
            'client_email': self.client_user.email,
            'beverage': 999
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_not_owner_of_establishment(self):
        other_partner = UserFactory(role="partner")
        self.client.force_authenticate(user=other_partner)
        data = {
            'client_email': self.client_user.email,
            'beverage': self.beverage.id
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'You are not the owner of the establishment linked to this beverage.' in response.data['error']

    def test_invalid_client_email(self):
        self.client.force_authenticate(user=self.partner)
        data = {
            'client_email': 'nonexistentemail@example.com',
            'beverage': self.beverage.id
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_order_statistics_view():
    user = UserFactory(role='partner')
    establishment = EstablishmentFactory(owner=user)
    category = CategoryFactory()
    beverage = BeverageFactory(category=category, establishment=establishment)
    order1 = OrderFactory(establishment=establishment, beverage=beverage)
    order2 = OrderFactory(establishment=establishment, beverage=beverage)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse('v1:order-statistics', kwargs={'establishment_id': establishment.id})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_orders'] == 2
    assert response.data['total_sum_prices'] is not None
    assert len(response.data['orders_by_category']) == 1
    assert response.data['orders_by_category'][0]['category'] == category.name
    assert response.data['orders_by_category'][0]['total_orders'] == 2

@pytest.mark.django_db
def test_incoming_orders_view():
    partner_user = UserFactory(role='partner')
    other_user = UserFactory(role='partner')
    establishment = EstablishmentFactory(owner=partner_user)
    beverage = BeverageFactory(establishment=establishment)
    order1 = OrderFactory(establishment=establishment, beverage=beverage, status='pending')
    order2 = OrderFactory(establishment=establishment, beverage=beverage, status='in_preparation')
    order3 = OrderFactory(establishment=establishment, beverage=beverage, status='completed')

    client = APIClient()
    client.force_authenticate(user=partner_user)

    url = reverse('v1:incoming-orders', kwargs={'establishment_id': establishment.id})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    client.force_authenticate(user=other_user)
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN