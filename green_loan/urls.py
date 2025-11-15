from django.urls import path
from . import views

urlpatterns = [
    path('green_loan/', views.green_loan_view, name='green_loan'),
    path('api/extract-payslip/', views.extract_payslip_text, name='extract_payslip'),
    path('api/analyze-payslip/', views.analyze_payslip, name='analyze_payslip'),
]