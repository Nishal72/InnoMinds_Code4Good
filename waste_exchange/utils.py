def business_to_dict(business):
    return {
        "id": business.id,
        "name": business.name,
        "waste": business.waste,
        "image": business.image.url if business.image else "",
        "phone": business.phone,
        "email": business.email,
        "latitude": business.latitude,
        "longitude": business.longitude,
    }
