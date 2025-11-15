from django.urls import reverse

def business_to_dict(business):
    return {
        "id": business.id,
        "name": business.name,
        "waste": business.waste,
        "phone": business.phone,
        "email": business.email,
        "latitude": business.latitude,
        "longitude": business.longitude,
        "category": business.category.name if business.category else "Uncategorized",
        "detail_url": reverse("business_detail", args=[business.id]),
    }

