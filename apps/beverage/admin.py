from django.contrib import admin

from apps.beverage.models import Category, Beverage
from apps.partner.models import Establishment

# Register your models here.
admin.site.register(Category)
admin.site.register(Beverage)
admin.site.register(Establishment)
