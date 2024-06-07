from django.contrib import admin

from apps.subscription.models import SubscriptionPlan, Subscription

# Register your models here.
admin.site.register(SubscriptionPlan)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active', 'is_trial')
    search_fields = ('user__email', 'plan__name')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['start_date', 'end_date']:
            formfield.widget.attrs['step'] = '0.001'
        return formfield


admin.site.register(SubscriptionPlan)
