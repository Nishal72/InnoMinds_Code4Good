from django.conf import settings
from django.shortcuts import render
from .models import Business
from .utils import business_to_dict
import json

# View for Waste Exchange page with Google Maps integration lololol
def waste_exchange_view(request):
    businesses = Business.objects.all()
    business_data = [business_to_dict(b) for b in businesses]

    return render(request, 'waste_exchange/waste_exchange.html', {

        "businesses_json": json.dumps(business_data),
        "GOOGLE_MAPS_KEY": settings.GOOGLE_MAPS_KEY
    })