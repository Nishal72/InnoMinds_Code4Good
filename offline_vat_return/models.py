from django.db import models

class VATReturn(models.Model):
    business_name = models.CharField(max_length=255)
    business_id = models.CharField(max_length=255)
    vat_collected = models.DecimalField(max_digits=10, decimal_places=2)
    vat_paid = models.DecimalField(max_digits=10, decimal_places=2)
    reporting_period = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    encrypted_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name} ({self.reporting_period})"
