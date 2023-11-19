from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    house_number = models.CharField(max_length=10)
    tenant_id = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=12)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
