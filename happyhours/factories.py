from datetime import timedelta

import factory
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.timezone import now
from factory.django import DjangoModelFactory

from apps.subscription.models import Subscription, SubscriptionPlan
from apps.user.models import ROLE_CHOICES
from apps.beverage.models import Category, Beverage
from apps.order.models import Order
from apps.partner.models import Establishment
from apps.feedback.models import Feedback, FeedbackAnswer
from faker import Faker

User = get_user_model()
fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ['email']
        skip_postgeneration_save = True

    email = factory.Faker('email')
    name = factory.Faker('name')
    date_of_birth = factory.Faker('date_of_birth', minimum_age=18, maximum_age=65)
    is_blocked = False
    created_at = factory.LazyFunction(timezone.now)
    modified_at = factory.LazyFunction(timezone.now)
    role = factory.Faker('random_element', elements=[choice[0] for choice in ROLE_CHOICES])
    max_establishments = 1

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted if extracted else 'defaultpassword123'
        self.set_password(password)
        if create:
            self.save()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')


class EstablishmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Establishment

    name = factory.Faker('company')
    location = factory.LazyFunction(lambda: Point(float(fake.longitude()), float(fake.latitude())))
    description = factory.Faker('paragraph')
    phone_number = factory.Faker('phone_number')
    address = factory.Faker('address')
    owner = factory.SubFactory(UserFactory)
    happyhours_start = '00:00:00'
    happyhours_end = '23:50:00'


class BeverageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Beverage

    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    description = factory.Faker('paragraph')
    availability_status = factory.Faker('boolean')
    category = factory.SubFactory(CategoryFactory)
    establishment = factory.SubFactory(EstablishmentFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    establishment = factory.SubFactory(EstablishmentFactory)
    beverage = factory.SubFactory(BeverageFactory)
    client = factory.SubFactory(UserFactory)
    # order_date = factory.LazyFunction(timezone.now)


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback

    user = factory.SubFactory(UserFactory)
    establishment = factory.SubFactory(EstablishmentFactory)
    text = factory.Faker('paragraph')


class FeedbackAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeedbackAnswer

    feedback = factory.SubFactory(FeedbackFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Faker('paragraph')


class SubscriptionPlanFactory(DjangoModelFactory):
    class Meta:
        model = SubscriptionPlan

    name = factory.Sequence(lambda n: f"Plan {n}")
    duration = factory.Iterator(['FT', '1M', '3M', '6M', '1Y'])
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    description = factory.Faker('text')
    free_trial_days = factory.Faker('random_int', min=0, max=30)


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(SubscriptionPlanFactory)
    start_date = factory.LazyFunction(now)
    end_date = None
    is_active = True
    is_trial = False

    @factory.post_generation
    def set_end_date(obj, create, extracted, **kwargs):
        if not obj.end_date:
            if obj.is_trial and obj.plan.free_trial_days:
                obj.end_date = obj.start_date + timedelta(days=obj.plan.free_trial_days)
            else:
                if obj.plan.duration == '1M':
                    obj.end_date = obj.start_date + relativedelta(months=1)
                elif obj.plan.duration == '3M':
                    obj.end_date = obj.start_date + relativedelta(months=3)
                elif obj.plan.duration == '6M':
                    obj.end_date = obj.start_date + relativedelta(months=6)
                elif obj.plan.duration == '1Y':
                    obj.end_date = obj.start_date + relativedelta(years=1)
            obj.save()
