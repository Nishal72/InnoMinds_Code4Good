# waste_exchange/forms.py
from django import forms
from .models import Business

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'waste', 'phone', 'email', 'latitude', 'longitude']
        widgets = {
            'waste': forms.Textarea(attrs={'rows': 3}),
            # Show lat/lng as read-only – they’ll be filled by clicking the map
            'latitude': forms.TextInput(attrs={'readonly': 'readonly'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
