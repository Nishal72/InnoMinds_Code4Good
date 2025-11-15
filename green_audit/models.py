from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class GreenAudit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    audit_text = models.TextField(help_text="Audit details or extracted text from image")
    image = models.ImageField(upload_to='audit_images/', null=True, blank=True)
    analysis_result = models.TextField(null=True, blank=True)
    
    # Electricity Bill Data
    bill_number = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    billing_period = models.CharField(max_length=100, null=True, blank=True)
    kwh_consumption = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total kWh consumed")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total bill amount in MUR")
    previous_reading = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_reading = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supply_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    energy_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Audit by {self.user.username if self.user else 'Anonymous'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def average_daily_kwh(self):
        """Calculate average daily consumption"""
        if self.kwh_consumption:
            return round(float(self.kwh_consumption) / 30, 2)  # Assuming 30 days billing period
        return 0
    
    @property
    def cost_per_kwh(self):
        """Calculate cost per kWh"""
        if self.kwh_consumption and self.total_amount and self.kwh_consumption > 0:
            return round(float(self.total_amount) / float(self.kwh_consumption), 2)
        return 0
