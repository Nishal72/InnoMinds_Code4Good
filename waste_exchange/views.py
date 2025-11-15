from django.shortcuts import render

# Create your views here.
def waste_exchange_view(request):
    return render(request, 'waste_exchange/(to-remname).html')