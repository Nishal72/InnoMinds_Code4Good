from django.contrib import admin
from .models import GreenAudit

# Register your models here.

@admin.register(GreenAudit)
class GreenAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'bill_number', 'kwh_consumption', 'total_amount', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('audit_text', 'analysis_result', 'user__username', 'bill_number', 'account_number')
    readonly_fields = ('created_at', 'updated_at', 'average_daily_kwh', 'cost_per_kwh')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Bill Information', {
            'fields': ('bill_number', 'account_number', 'billing_period', 'image')
        }),
        ('Consumption Data', {
            'fields': ('kwh_consumption', 'previous_reading', 'current_reading', 'average_daily_kwh')
        }),
        ('Cost Data', {
            'fields': ('total_amount', 'supply_charge', 'energy_charge', 'cost_per_kwh')
        }),
        ('Analysis', {
            'fields': ('audit_text', 'analysis_result')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
