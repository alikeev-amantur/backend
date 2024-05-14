from django.db import models


class BeverageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(establishment__owner__is_blocked=False)

