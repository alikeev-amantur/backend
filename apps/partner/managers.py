from django.db import models


class EstablishmentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(owner__is_blocked=False)
