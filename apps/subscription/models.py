from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.timezone import now

from apps.user.models import User


# Create your models here.
class SubscriptionPlan(models.Model):
    DURATION_CHOICES = [
        ('FT', 'Free Trial'),
        ('1M', '1 Month'),
        ('3M', '3 Months'),
        ('6M', '6 Months'),
        ('1Y', '1 Year'),
    ]

    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=2, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    free_trial_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.end_date:
            if self.is_trial and self.plan.free_trial_days:
                self.end_date = self.start_date + timedelta(days=self.plan.free_trial_days)
            else:
                if self.plan.duration == '1M':
                    self.end_date = self.start_date + relativedelta(months=1)
                elif self.plan.duration == '3M':
                    self.end_date = self.start_date + relativedelta(months=3)
                elif self.plan.duration == '6M':
                    self.end_date = self.start_date + relativedelta(months=6)
                elif self.plan.duration == '1Y':
                    self.end_date = self.start_date + relativedelta(years=1)

        super(Subscription, self).save(*args, **kwargs)

    def deactivate(self):
        if self.end_date and self.end_date < now():
            self.is_active = False
            self.save()

    def __str__(self):
        plan_name = self.plan.name if self.plan else 'None'
        return f"{self.user.email} - {plan_name} {'(Trial)' if self.is_trial else ''}"
