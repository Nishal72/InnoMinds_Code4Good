from django.shortcuts import render

# Create your views here.

def green_loan_view(request):
    return render(request, 'green_loan/green_loan.html')