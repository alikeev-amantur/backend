import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from apps.order.models import Order
from happyhours.factories import (
    UserFactory,
    BeverageFactory,
    EstablishmentFactory,
    OrderFactory, SubscriptionFactory,
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
        self.partner_order_history_url = reverse("v1:partner-order-history-list")

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


