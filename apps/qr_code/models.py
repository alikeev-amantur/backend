from django.db import models

from apps.partner.models import Establishment


# Create your models here.
class QRCode(models.Model):
    establishment = models.OneToOneField(Establishment, on_delete=models.CASCADE, related_name='qr_code')
    qr_code_image = models.ImageField(upload_to='qr_codes/')

    def __str__(self):
        return f"QR Code for {self.establishment.name}"
