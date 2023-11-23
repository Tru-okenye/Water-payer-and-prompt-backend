from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    house_number = models.CharField(max_length=10)
    tenant_id = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=12)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

class PaymentTransaction(models.Model):
    tenant_id = models.CharField(max_length=20) 
    checkout_request_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PaymentTransaction for Tenant ID {self.tenant_id}"