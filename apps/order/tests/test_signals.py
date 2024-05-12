import pytest
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async

from happyhours.factories import UserFactory, EstablishmentFactory, BeverageFactory, OrderFactory
from ..models import Order, Establishment
from unittest.mock import patch

User = get_user_model()


@pytest.mark.django_db
def test_order_notifications():
    user = UserFactory.create()
    client = UserFactory.create()
    establishment = EstablishmentFactory.create(owner=user)
    beverage = BeverageFactory.create(establishment=establishment)
    order = OrderFactory.build(beverage=beverage, establishment=establishment, client=client)

    channel_layer = get_channel_layer()
    with patch('channels.layers.get_channel_layer') as channel_layer_mock:
        channel_layer_mock.return_value = channel_layer

        with patch.object(channel_layer, 'group_send') as mock_group_send:
            order.save()

            mock_group_send.assert_called_once()
            called_args, _ = mock_group_send.call_args
            assert called_args[0] == f'order_{establishment.id}'
            assert called_args[1]['type'] == 'order_message'
            assert 'New order created' in called_args[1]['details']


            mock_group_send.reset_mock()

            order.status = 'completed'
            order.save()

            mock_group_send.assert_called_once()
            called_args, _ = mock_group_send.call_args
            assert 'Order updated' in called_args[1]['details']
