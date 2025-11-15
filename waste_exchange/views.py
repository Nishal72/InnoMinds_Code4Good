from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

from .models import Business, BusinessImage
from .utils import business_to_dict
from .forms import BusinessForm
import json


def waste_exchange_view(request):
    businesses = Business.objects.all()
    business_data = [business_to_dict(b) for b in businesses]

    return render(request, 'waste_exchange/waste_exchange.html', {
        "businesses_json": json.dumps(business_data),
        "GOOGLE_MAPS_KEY": settings.GOOGLE_MAPS_KEY,
    })


def register_business(request):
    if request.method == "POST":
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save()

            # Handle multiple uploaded images
            for image_file in request.FILES.getlist('images'):
                BusinessImage.objects.create(
                    business=business,
                    image=image_file
                )

            return redirect('business_detail', pk=business.pk)
    else:
        form = BusinessForm()

    return render(request, 'waste_exchange/register_business.html', {
        "form": form,
        "GOOGLE_MAPS_KEY": settings.GOOGLE_MAPS_KEY,
    })


def business_detail(request, pk):
    business = get_object_or_404(Business, pk=pk)
    images = business.images.all()

    return render(request, 'waste_exchange/business_detail.html', {
        "business": business,
        "images": images,
    })
