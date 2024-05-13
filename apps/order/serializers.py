from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Order

from .schema_definitions import order_serializer_schema, order_history_serializer_schema
from .utils import validate_order_happyhours, validate_order_per_hour, validate_order_per_day

User = get_user_model()


@order_serializer_schema
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'client', 'beverage', 'establishment', 'order_date']
        read_only_fields = ['client', 'establishment']

    def validate(self, data):
        establishment = data.get('beverage').establishment
        client = self.context['request'].user
        validate_order_happyhours(establishment)
        validate_order_per_hour(client)
        validate_order_per_day(client, establishment)

        return data


class OwnerOrderSerializer(OrderSerializer):
    client_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'client', 'beverage', 'establishment', 'order_date', 'client_email']
        read_only_fields = ['client', 'establishment']

    def validate(self, data):
        client_email = data.pop('client_email', None)
        try:
            client = User.objects.get(email=client_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'client_email': 'No user found with this email address.'})
        data['client'] = client

        establishment = data.get('beverage').establishment
        validate_order_happyhours(establishment)
        validate_order_per_hour(client)
        validate_order_per_day(client, establishment)

        return data


@order_history_serializer_schema
class OrderHistorySerializer(serializers.ModelSerializer):
    establishment_name = serializers.CharField(
        source="establishment.name", read_only=True
    )
    beverage_name = serializers.CharField(source="beverage.name", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_date", "establishment_name", "beverage_name", "client", "status"]
