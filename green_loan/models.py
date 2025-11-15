from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class GreenLoan(models.Model):
    """Model to store green loan applications and analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='green_loans')
    
    # Payslip data
    payslip_text = models.TextField(blank=True, help_text="Extracted text from payslip")
    payslip_image = models.ImageField(upload_to='payslip_images/', null=True, blank=True)
    
    # Extracted payslip information
    employee_name = models.CharField(max_length=255, blank=True)
    employee_id = models.CharField(max_length=100, blank=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    
    # Loan analysis result
    loan_suggestion = models.TextField(blank=True, help_text="AI-generated loan suggestion")
    loan_available = models.BooleanField(default=False)
    loan_type = models.CharField(max_length=255, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Annual interest rate in percentage")
    max_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    loan_term_months = models.IntegerField(null=True, blank=True, help_text="Loan term in months")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Green Loan Application'
        verbose_name_plural = 'Green Loan Applications'
    
    def __str__(self):
        return f"Loan Application by {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
    
    @property
    def monthly_payment(self):
        """Calculate estimated monthly payment"""
        if self.max_loan_amount and self.interest_rate and self.loan_term_months:
            # Simple monthly payment calculation
            principal = float(self.max_loan_amount)
            rate = float(self.interest_rate) / 100 / 12  # Monthly interest rate
            n = self.loan_term_months
            
            if rate > 0:
                payment = principal * (rate * (1 + rate)**n) / ((1 + rate)**n - 1)
                return Decimal(str(round(payment, 2)))
        return None
