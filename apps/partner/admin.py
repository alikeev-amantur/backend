from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Establishment


class EstablishmentAdmin(GISModelAdmin):
    pass


admin.site.register(Establishment, EstablishmentAdmin)
