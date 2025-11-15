from django.urls import path
from . import views

urlpatterns = [
    path('', views.green_audit_view, name='green_audit'),
    path('api/analyze/', views.analyze_audit, name='analyze_audit'),
    path('api/extract-text/', views.extract_text_from_image, name='extract_text'),
]