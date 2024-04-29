from rest_framework import serializers
from .models import Order, Establishment, Beverage, User
import datetime


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'establishment', 'beverage', 'client', 'order_date', 'establihsment_name', 'beverage_name',
                  'client_details']

    def validate_order_date(self, value):
        # Check if the order is within happy hours
        current_time = value.time()
        establishment_id = self.initial_data.get('establishment')
        if establishment_id:
            establishment = Establishment.objects.get(id=establishment_id)
            if not (establishment.happy_hours_start <= current_time <= establishment.happy_hours_end):
                raise serializers.ValidationError("You can only place an order during happy hours.")
        return value

    def validate_client_and_order_date_for_hourly_limit(self, data):
        # Ensure one order per hour at any establishment
        client = data['client']
        order_date = data['order_date']
        hour_start = datetime.datetime.combine(order_date.date(),
                                               order_date.time().replace(minute=0, second=0, microsecond=0))
        hour_end = hour_start + datetime.timedelta(hours=1)

        existing_order_same_hour = Order.objects.filter(
            client=client,
            order_date__range=(hour_start, hour_end)
        ).exists()

        if existing_order_same_hour:
            raise serializers.ValidationError("You can only place one order per hour at any establishment.")

    def validate_client_and_order_date_for_daily_limit(self, data):
        # Ensure one order per day per establishment
        client = data['client']
        establishment = data['establishment']
        order_date = data['order_date']
        today_min = datetime.datetime.combine(order_date.date(), datetime.time.min)
        today_max = datetime.datetime.combine(order_date.date(), datetime.time.max)

        existing_order_same_day = Order.objects.filter(
            client=client,
            establishment=establishment,
            order_date__range=(today_min, today_max)
        ).exists()

        if existing_order_same_day:
            raise serializers.ValidationError("You can only place one order per establishment per day.")

    def validate(self, data):
        self.validate_client_and_order_date_for_hourly_limit(data)
        self.validate_client_and_order_date_for_daily_limit(data)
        return data
