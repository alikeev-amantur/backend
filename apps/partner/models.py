from django.db import models


class Establishment(models.Model):
    """
    Represents an establishment model
    """
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    phone_number = models.CharField(max_length=255)

    def __str__(self):
        return 'Establishment: ' + self.name
