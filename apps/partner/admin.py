from django.contrib import admin
from django.contrib.gis import admin as gis_admin

from .models import Establishment


class EstablishmentAdmin(gis_admin.OSMGeoAdmin):
    list_display = [
        "name", "id", "owner",
    ]


admin.site.register(Establishment, EstablishmentAdmin)
