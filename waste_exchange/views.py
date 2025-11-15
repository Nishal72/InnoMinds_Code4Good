from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

from .models import Business, BusinessImage, Category
from .utils import business_to_dict
from .forms import BusinessForm
import json

from django.core.mail import send_mail
from django.contrib import messages

def waste_exchange_view(request):
    businesses = Business.objects.all()
    categories = Category.objects.all()
    business_data = [business_to_dict(b) for b in businesses]

    return render(request, 'waste_exchange/waste_exchange.html', {
        "businesses_json": json.dumps(business_data),
        "categories": categories,
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


def request_quote(request, pk):
    business = get_object_or_404(Business, pk=pk)

    if request.method == "POST":
        user_name = request.POST.get("name")
        user_email = request.POST.get("email")
        message_body = request.POST.get("message")

        subject = f"Quotation Request from {user_name}"
        message = (
            f"You have received a new quotation request.\n\n"
            f"Name: {user_name}\n"
            f"Email: {user_email}\n\n"
            f"Message:\n{message_body}"
        )

        send_mail(
            subject,
            message,
            user_email,               # from
            [business.email],         # to business owner
        )

        messages.success(request, "Your quotation request has been sent successfully!")
        return redirect("business_detail", pk=pk)

    return redirect("business_detail", pk=pk)
