from django.urls import path
from .views import vat_form, decrypt_tool

urlpatterns = [
    path("", vat_form, name="offline_vat_form"),
    path("decrypt/", decrypt_tool, name="offline_vat_decrypt"),
]
