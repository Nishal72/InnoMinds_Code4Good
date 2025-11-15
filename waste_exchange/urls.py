from django.urls import path
from . import views

urlpatterns = [
    path('', views.waste_exchange_view, name='waste_exchange'),
    path('register/', views.register_business, name='register_business'),
    path('<int:pk>/', views.business_detail, name='business_detail'),
]