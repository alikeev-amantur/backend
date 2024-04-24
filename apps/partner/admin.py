from django.contrib import admin

from .models import Establishment, QRCode

admin.site.register(Establishment)
admin.site.register(QRCode)
