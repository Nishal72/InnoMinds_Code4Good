from django.contrib import admin
from .models import GreenLoan

@admin.register(GreenLoan)
class GreenLoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_name', 'monthly_salary', 'loan_type', 'loan_available', 'max_loan_amount', 'created_at')
    list_filter = ('loan_available', 'loan_type', 'created_at')
    search_fields = ('user__username', 'employee_name', 'employee_id', 'company_name')
    readonly_fields = ('created_at', 'updated_at', 'monthly_payment')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Payslip Data', {
            'fields': ('payslip_image', 'payslip_text')
        }),
        ('Employee Information', {
            'fields': ('employee_name', 'employee_id', 'monthly_salary', 'company_name', 'designation')
        }),
        ('Loan Analysis', {
            'fields': ('loan_suggestion', 'loan_available', 'loan_type', 'interest_rate', 'max_loan_amount', 'loan_term_months', 'monthly_payment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
