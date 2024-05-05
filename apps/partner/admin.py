from django.contrib import admin

from .models import Establishment, QRCode, Feedback, FeedbackAnswer

admin.site.register(Establishment)
admin.site.register(QRCode)
admin.site.register(Feedback)
admin.site.register(FeedbackAnswer)
