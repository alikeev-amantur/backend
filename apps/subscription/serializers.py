from django.utils.timezone import now
from rest_framework import serializers
from .models import Subscription, SubscriptionPlan


class FreeTrialSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField()

    class Meta:
        model = Subscription
        fields = ['plan_id']

    def validate_plan_id(self, value):
        try:
            SubscriptionPlan.objects.get(id=value)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Subscription plan does not exist.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        plan_id = validated_data['plan_id']
        plan = SubscriptionPlan.objects.get(id=plan_id)

        if Subscription.objects.filter(user=user, plan=plan, is_trial=True).exists():
            raise serializers.ValidationError('User has already used a free trial for this plan')

        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            start_date=now(),
            is_trial=True
        )
        return subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'duration', 'price', 'description', 'free_trial_days']

    def validate(self, data):
        if data.get('free_trial_days', 0) > 0 and data.get('price', 1) != 0:
            raise serializers.ValidationError("Price must be zero for free trial plans.")
        if data.get('duration') != 'FT' and data.get('free_trial_days', 0) > 0:
            raise serializers.ValidationError('Duration must be FT for free trial days')
        return data

    def validate_duration(self, value):
        valid_durations = dict(SubscriptionPlan.DURATION_CHOICES).keys()
        if value not in valid_durations:
            raise serializers.ValidationError("Invalid duration. Choose from 1 Month, 3 Months, 6 Months, or 1 Year.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    start_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f%z')
    end_date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f%z')

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'is_active', 'is_trial']
