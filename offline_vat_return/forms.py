from django import forms
from .models import VATReturn

class VATReturnForm(forms.ModelForm):
    class Meta:
        model = VATReturn
        fields = [
            "business_name",
            "business_id",
            "vat_collected",
            "vat_paid",
            "reporting_period",
            "phone_number",
        ]
        widgets = {
            "business_name": forms.TextInput(attrs={"class": "form-control"}),
            "business_id": forms.TextInput(attrs={"class": "form-control"}),
            "vat_collected": forms.NumberInput(attrs={"class": "form-control"}),
            "vat_paid": forms.NumberInput(attrs={"class": "form-control"}),
            "reporting_period": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }
