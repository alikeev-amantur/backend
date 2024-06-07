from django.contrib import admin

from apps.subscription.models import SubscriptionPlan, Subscription

# Register your models here.
admin.site.register(SubscriptionPlan)
admin.site.register(Subscription)
