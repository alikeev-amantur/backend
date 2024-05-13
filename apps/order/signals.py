from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.cache import cache


@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group_name = f'order_{instance.establishment.id}'

    message = {
        "type": "order_message",
        "order_id": instance.id,
        "establishment_id": instance.establishment.id,
        "status": instance.status,
        "client": instance.client.id,
        "details": f"New order created: {instance.id}" if created else f"Order updated: {instance.id}"
    }

    # Send the message to the group
    async_to_sync(channel_layer.group_send)(
        group_name,
        message
    )
