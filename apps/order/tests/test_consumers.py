import pytest
import json

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from happyhours.asgi import application
from happyhours.factories import UserFactory, EstablishmentFactory, BeverageFactory, OrderFactory


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_order_consumer():
    user = await database_sync_to_async(UserFactory)(role='partner')
    establishment = await database_sync_to_async(EstablishmentFactory)(owner=user)
    beverage = await database_sync_to_async(BeverageFactory)(establishment=establishment)
    order = await database_sync_to_async(OrderFactory)(beverage=beverage, establishment=establishment)

    token = AccessToken.for_user(user)

    communicator = WebsocketCommunicator(
        application, f"/ws/orders/?token={str(token)}"
    )
    connected, subprotocol = await communicator.connect()
    assert connected, "Connection to websocket failed"

    group_name = f'order_{establishment.id}'
    message = {
        'type': 'order_message',
        'order_id': order.id,
        'establishment_id': establishment.id,
        'status': order.status,
        'client': order.client.id,
        'details': f"New order created: {order.id}"
    }
    channel_layer = get_channel_layer()
    await channel_layer.group_send(group_name, message)
    response = await communicator.receive_json_from()
    assert response == message

    await communicator.send_json_to({
        'type': 'update_order',
        'order_id': order.id,
        'status': 'completed'
    })

    # Disconnect
    await communicator.disconnect()

@pytest.fixture
def user():
    return UserFactory()

