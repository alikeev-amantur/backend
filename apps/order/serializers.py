from django.utils import timezone
from rest_framework import serializers
from .models import Order, Establishment
import datetime


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'establishment', 'beverage', 'client', 'order_date']
        read_only_fields = ['establishment']

    def get_default_establishment(self, beverage):
        # Get the establishment associated with the beverage
        return beverage.establishment

    def validate_order_date(self, value):
        current_time = timezone.now()
        establishment = self.get_default_establishment(self.initial_data['beverage'])
        if not (establishment.happy_hours_start <= current_time.time() <= establishment.happy_hours_end):
            raise serializers.ValidationError("You can only place an order during happy hours.")
        return value

    def validate_order_per_hour(self, client):
        # Ensure one order per hour at any establishment
        current_time = timezone.now()
        hour_start = datetime.datetime.combine(current_time.date(),
                                               current_time.time().replace(minute=0, second=0, microsecond=0))
        hour_end = hour_start + datetime.timedelta(hours=1)

        existing_order_same_hour = Order.objects.filter(
            client=client,
            order_date__range=(hour_start, hour_end)
        ).exists()

        if existing_order_same_hour:
            raise serializers.ValidationError("You can only place one order per hour at any establishment.")

    def validate_order_per_day(self, client, establishment):
        # Ensure one order per day per establishment
        current_time = timezone.now()
        today_min = datetime.datetime.combine(current_time.date(), datetime.time.min)
        today_max = datetime.datetime.combine(current_time.date(), datetime.time.max)

        existing_order_same_day = Order.objects.filter(
            client=client,
            establishment=establishment,
            order_date__range=(today_min, today_max)
        ).exists()

        if existing_order_same_day:
            raise serializers.ValidationError("You can only place one order per establishment per day.")

    def validate(self, data):
        # Automate providing client and establishment
        data['client'] = self.context['request'].user
        data['establishment'] = self.get_default_establishment(data['beverage'])

        client = data['client']
        establishment = data['establishment']

        self.validate_order_per_hour(client)
        self.validate_order_per_day(client, establishment)

        return data


class OrderHistorySerializer(serializers.ModelSerializer):
    establishment_name = serializers.CharField(source='establishment.name', read_only=True)
    beverage_name = serializers.CharField(source='beverage.name', read_only=True)
    client_details = serializers.HyperlinkedRelatedField(
        view_name='v1:user-detail',
        read_only=True,
        source='client'
    )

    class Meta:
        model = Order
        fields = ['id', 'order_date', 'establishment_name', 'beverage_name',
                  'client_details']
