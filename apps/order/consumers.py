import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, TokenError

from .models import Order

from ..partner.models import Establishment


class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope['query_string'].decode().split('token=')[1]
        user = await self.get_user_from_token(token)
        if user is not None and user.role == "partner":
            self.user = user
            self.groups = []
            establishments = await self.get_user_establishments(user)
            for establishment in establishments:
                group_name = f'order_{establishment.id}'
                self.groups.append(group_name)
                await self.channel_layer.group_add(group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'update_order':
            order_id = text_data_json.get('order_id')
            new_status = text_data_json.get('status')
            updated = await self.update_order_status(order_id, new_status)
            if not updated:
                await self.send(text_data=json.dumps({
                    'error': 'Failed to update order. You might not have permission or the order does not exist.'
                }))

    async def order_message(self, event):
        # Forward order details to the client
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'order_id': event['order_id'],
            'establishment_id': event['establishment_id'],
            'status': event['status'],
            'client': event['client'],
            'details': event['details']
        }))

    @database_sync_to_async
    def get_user_establishments(self, user):
        return list(Establishment.objects.filter(owner=user))

    @database_sync_to_async
    def update_order_status(self, order_id, status):
        try:
            order = Order.objects.select_related('establishment').get(id=order_id, establishment__owner=self.user)
            order.status = status
            order.save()
            return True
        except Order.DoesNotExist:
            return False

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            valid_token = AccessToken(token)
            user_id = valid_token['user_id']
            user = get_user_model().objects.get(id=user_id)
            return user
        except TokenError as e:
            return None
