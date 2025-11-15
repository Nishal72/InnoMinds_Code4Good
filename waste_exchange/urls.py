from django.urls import path
from . import views

urlpatterns = [
    path('', views.waste_exchange_view, name='waste_exchange'),
]