from django.urls import path
from . import views

urlpatterns = [
    path('green_loan/', views.green_loan_view, name='green_loan'),
]