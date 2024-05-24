import pytest
from datetime import timedelta
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from happyhours.factories import UserFactory, SubscriptionPlanFactory, SubscriptionFactory
from ..models import Subscription, SubscriptionPlan

@pytest.mark.django_db
def test_subscription_plan_creation():
    plan = SubscriptionPlanFactory()
    assert SubscriptionPlan.objects.count() == 1
    assert plan.name is not None
    assert plan.duration in ['FT', '1M', '3M', '6M', '1Y']

@pytest.mark.django_db
def test_subscription_creation():
    user = UserFactory()
    plan = SubscriptionPlanFactory(duration='1M')
    subscription = SubscriptionFactory(user=user, plan=plan)
    assert Subscription.objects.count() == 1
    assert subscription.user == user
    assert subscription.plan == plan
    assert subscription.is_active
    assert subscription.end_date == subscription.start_date + relativedelta(months=1)

@pytest.mark.django_db
def test_free_trial_subscription_creation():
    user = UserFactory()
    plan = SubscriptionPlanFactory(duration='FT', free_trial_days=14)
    subscription = SubscriptionFactory(user=user, plan=plan, is_trial=True)
    assert Subscription.objects.count() == 1
    assert subscription.user == user
    assert subscription.plan == plan
    assert subscription.is_trial
    assert subscription.is_active
    assert subscription.end_date == subscription.start_date + timedelta(days=14)

@pytest.mark.django_db
def test_subscription_deactivation():
    user = UserFactory()
    plan = SubscriptionPlanFactory(duration='1M')
    subscription = SubscriptionFactory(user=user, plan=plan)
    subscription.end_date = now() - timedelta(days=1)
    subscription.save()
    subscription.deactivate()
    assert not subscription.is_active
