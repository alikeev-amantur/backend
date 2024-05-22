from channels.layers import get_channel_layer
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
import datetime

from apps.order.models import Order

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


def validate_order_happyhours(establishment):
    if not establishment.is_happy_hour():
        raise serializers.ValidationError("Order can only be placed during happy hours.")


def validate_order_per_hour(client):
    one_hour_ago = timezone.localtime() - datetime.timedelta(hours=1)
    if Order.objects.filter(client=client, order_date__gte=one_hour_ago).exclude(status='cancelled').exists():
        raise serializers.ValidationError("You can only place one order per hour.")


def validate_order_per_day(client, establishment):
    today_min = datetime.datetime.combine(timezone.localtime().date(), datetime.time.min)
    today_max = datetime.datetime.combine(timezone.localtime().date(), datetime.time.max)
    if Order.objects.filter(client=client, establishment=establishment,
                            order_date__range=(today_min, today_max)).exclude(status='cancelled').exists():
        raise serializers.ValidationError("You can only place one order per establishment per day.")


