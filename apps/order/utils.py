from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


async def send_order_notification(order):
    channel_layer = get_channel_layer()
    message = {
        'type': 'order_message',
        'order_id': order.id,
        'establishment_id': order.establishment.id,
        'status': order.status,
        'details': f"New order {order.id} for {order.beverage.name}"
    }
    group_name = f'order_{order.establishment_id}'
    await channel_layer.group_send(group_name, message)