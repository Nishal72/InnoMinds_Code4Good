from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import GreenLoan
import json
import os
import re
from decimal import Decimal
import easyocr
import cv2
import numpy as np
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize EasyOCR reader (singleton pattern for efficiency)
reader = None

def get_ocr_reader():
    """Get or initialize EasyOCR reader"""
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'])
    return reader

def green_loan_view(request):
    """Main green loan page view"""
    # Get recent loan applications for the user
    recent_loans = []
    total_applications = 0
    approved_count = 0
    
    if request.user.is_authenticated:
        recent_loans = GreenLoan.objects.filter(user=request.user)[:5]
        total_applications = GreenLoan.objects.filter(user=request.user).count()
        approved_count = GreenLoan.objects.filter(user=request.user, loan_available=True).count()
    
    context = {
        'recent_loans': recent_loans,
        'total_applications': total_applications,
        'approved_count': approved_count,
    }
    return render(request, 'green_loan/green_loan.html', context)

@csrf_exempt
def extract_payslip_text(request):
    """Extract text from uploaded payslip image using EasyOCR"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=400)
    
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)
    
    try:
        image_file = request.FILES['image']
        
        # Save image temporarily
        image_path = default_storage.save(f'temp_payslip/{image_file.name}', ContentFile(image_file.read()))
        full_path = default_storage.path(image_path)
        
        # Read image with OpenCV
        image = cv2.imread(full_path)
        
        # Get OCR reader and extract text
        ocr_reader = get_ocr_reader()
        results = ocr_reader.readtext(image)
        
        # Combine all detected text
        extracted_text = ' '.join([text[1] for text in results])
        
        # Clean up temporary file
        if os.path.exists(full_path):
            os.remove(full_path)
        
        return JsonResponse({
            'success': True,
            'extracted_text': extracted_text
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def extract_payslip_data(text):
    """Extract structured data from payslip text using regex patterns"""
    data = {
        'employee_name': '',
        'employee_id': '',
        'monthly_salary': None,
        'company_name': '',
        'designation': ''
    }
    
    # Clean the text - remove extra spaces and normalize
    text = ' '.join(text.split())
    
    # Pattern for salary (various formats) - improved to capture larger numbers
    salary_patterns = [
        r'(?:gross\s*pay|basic\s*salary|net\s*pay|monthly\s*salary|salary|total\s*pay)[:\s]*(?:MUR|Rs\.?|₨)?\s*([\d,]+(?:\.\d{1,2})?)',
        r'(?:MUR|Rs\.?|₨)\s*([\d,]{4,}(?:\.\d{1,2})?)',  # At least 4 digits
        r'(?:pay|salary)[:\s]*([\d,]{4,}(?:\.\d{1,2})?)',
        r'\b([\d,]{5,}(?:\.\d{1,2})?)\s*(?:MUR|Rs\.?|₨|rupees)',  # 5+ digits followed by currency
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            salary_str = match.group(1).replace(',', '').replace(' ', '')
            try:
                salary_value = Decimal(salary_str)
                # Only accept reasonable salary values (between 5,000 and 500,000 MUR)
                if 5000 <= salary_value <= 500000:
                    data['monthly_salary'] = salary_value
                    break
            except:
                pass
    
    # Pattern for employee name
    name_patterns = [
        r'(?:employee\s*name|name)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'(?:mr|mrs|ms|miss)[.\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['employee_name'] = match.group(1).strip()
            break
    
    # Pattern for employee ID
    id_patterns = [
        r'(?:employee\s*id|emp\s*id|id)[:\s]*([A-Z0-9-]+)',
        r'(?:emp|employee)[:\s]*([0-9]+)',
    ]
    
    for pattern in id_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['employee_id'] = match.group(1).strip()
            break
    
    # Pattern for company name
    company_patterns = [
        r'(?:company|employer)[:\s]*([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Inc|Corporation)?)',
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['company_name'] = match.group(1).strip()
            break
    
    # Pattern for designation
    designation_patterns = [
        r'(?:designation|position|title)[:\s]*([A-Z][A-Za-z\s]+)',
    ]
    
    for pattern in designation_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['designation'] = match.group(1).strip()
            break
    
    return data

@csrf_exempt
def analyze_payslip(request):
    """Analyze payslip and provide green loan suggestions using OpenAI"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=400)
    
    try:
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            payslip_text = data.get('payslip_text', '')
            image_data = data.get('image')
        else:
            payslip_text = request.POST.get('payslip_text', '')
            image_data = request.FILES.get('image')
        
        if not payslip_text:
            return JsonResponse({'error': 'No payslip text provided'}, status=400)
        
        # Extract structured data from payslip
        extracted_data = extract_payslip_data(payslip_text)
        
        # Create detailed prompt for OpenAI
        prompt = f"""
You are a financial advisor specializing in green loans for eco-friendly projects in Mauritius. 
Analyze the following payslip details and provide a comprehensive loan recommendation.

PAYSLIP DATA:
{payslip_text[:2000]}

EXTRACTED INFORMATION:
- Employee Name: {extracted_data.get('employee_name', 'Not found')}
- Employee ID: {extracted_data.get('employee_id', 'Not found')}
- Monthly Salary: MUR {extracted_data.get('monthly_salary', 'Not found')}
- Company: {extracted_data.get('company_name', 'Not found')}
- Designation: {extracted_data.get('designation', 'Not found')}

GREEN LOAN CONTEXT IN MAURITIUS:
- Green loans fund solar panels, energy-efficient upgrades, electric vehicles, rainwater harvesting, etc.
- Typical interest rates: 4-8% per annum for green projects
- Loan amounts: Up to 5x monthly salary for salaried employees
- Loan terms: 3-15 years depending on project and salary
- Banks in Mauritius: MCB, SBM, ABC Banking, BOM, HSBC offer green loans
- Government incentives: VAT exemption on solar equipment, subsidies available

ANALYSIS REQUIREMENTS:
1. Loan Eligibility: Is the applicant eligible? (Consider if salary is identifiable)
2. Loan Type: Recommend specific green loan type (Solar, Energy Efficiency, EV, etc.)
3. Interest Rate: Provide realistic annual rate (4-8%) based on salary and employment
4. Maximum Loan Amount: Calculate based on 3-5x monthly salary
5. Loan Term: Suggest term in years (5-15 years typical)
6. Monthly Payment: Estimate monthly payment amount
7. Recommended Banks: List 2-3 Mauritian banks offering best rates
8. Documentation Needed: List required documents
9. Tips: Provide 3 practical tips for approval
10. Eco-Impact: Estimate CO2 reduction potential

FORMAT YOUR RESPONSE AS JSON:
{{
    "loan_available": true/false,
    "loan_type": "Solar Panel Installation Loan / Energy Efficiency Loan / EV Loan / etc.",
    "interest_rate": 5.5,
    "max_loan_amount": 500000,
    "loan_term_years": 10,
    "monthly_payment": 5500,
    "eligibility_reason": "Brief explanation of eligibility",
    "recommended_banks": [
        {{"name": "MCB Bank", "rate": "5.25%", "terms": "Up to 15 years", "special": "No processing fees for solar loans"}},
        {{"name": "SBM Bank", "rate": "5.75%", "terms": "Up to 10 years", "special": "Fast approval in 48 hours"}}
    ],
    "documentation": ["Payslips (last 3 months)", "National ID", "Bank statements (6 months)", "Proof of residence", "Project quotation"],
    "approval_tips": [
        "Maintain good credit score above 650",
        "Provide detailed project quotations from certified vendors",
        "Show stable employment history (minimum 1 year)"
    ],
    "eco_impact": "Installing 5kW solar system can reduce CO2 emissions by approximately 3.5 tons annually and save MUR 45,000 in electricity costs over 10 years.",
    "detailed_analysis": "Comprehensive narrative analysis explaining the recommendation, calculations, and benefits."
}}

Provide realistic numbers based on the salary information. If salary cannot be determined, use conservative estimates.
"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful financial advisor specializing in green loans and sustainable finance in Mauritius."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                loan_data = json.loads(json_match.group())
            else:
                # Fallback: create structured response from text
                loan_data = {
                    'loan_available': 'eligible' in ai_response.lower() or 'approved' in ai_response.lower(),
                    'detailed_analysis': ai_response
                }
        except:
            loan_data = {'detailed_analysis': ai_response}
        
        # Save to database if user is authenticated
        if request.user.is_authenticated and image_data:
            # Save image
            if isinstance(image_data, str):
                # Base64 image (from JSON)
                pass  # Handle base64 if needed
            else:
                # File upload
                loan_record = GreenLoan.objects.create(
                    user=request.user,
                    payslip_text=payslip_text,
                    payslip_image=image_data,
                    employee_name=extracted_data.get('employee_name', ''),
                    employee_id=extracted_data.get('employee_id', ''),
                    monthly_salary=extracted_data.get('monthly_salary'),
                    company_name=extracted_data.get('company_name', ''),
                    designation=extracted_data.get('designation', ''),
                    loan_suggestion=ai_response,
                    loan_available=loan_data.get('loan_available', False),
                    loan_type=loan_data.get('loan_type', ''),
                    interest_rate=loan_data.get('interest_rate'),
                    max_loan_amount=loan_data.get('max_loan_amount'),
                    loan_term_months=loan_data.get('loan_term_years', 10) * 12 if loan_data.get('loan_term_years') else None
                )
        
        # Return analysis
        return JsonResponse({
            'success': True,
            'analysis': loan_data,
            'extracted_data': extracted_data
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)