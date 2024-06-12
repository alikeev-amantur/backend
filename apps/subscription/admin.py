from django.contrib import admin

from apps.subscription.models import SubscriptionPlan, Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'plan',
        'start_date',
        'end_date',
        'is_active',
        'is_trial',
    )


admin.site.register(SubscriptionPlan)
admin.site.register(Subscription, SubscriptionAdmin)
