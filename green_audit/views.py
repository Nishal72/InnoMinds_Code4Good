from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import json
import re
from decimal import Decimal, InvalidOperation
from openai import OpenAI
from dotenv import load_dotenv
from .models import GreenAudit

# Load environment variables
load_dotenv()

# Create your views here.
def green_audit_view(request):
    """Main view for the green audit page"""
    # Get recent audits for the user
    recent_audits = None
    total_kwh = 0
    total_cost = 0
    
    if request.user.is_authenticated:
        recent_audits = GreenAudit.objects.filter(user=request.user)[:10]
        # Calculate totals
        for audit in recent_audits:
            if audit.kwh_consumption:
                total_kwh += float(audit.kwh_consumption)
            if audit.total_amount:
                total_cost += float(audit.total_amount)
    
    context = {
        'recent_audits': recent_audits,
        'total_kwh': round(total_kwh, 2),
        'total_cost': round(total_cost, 2),
    }
    return render(request, 'green_audit/green_audit.html', context)


@csrf_exempt
def analyze_audit(request):
    """API endpoint to analyze audit data using OpenAI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            audit_text = data.get('audit_text', '').strip()
            
            if not audit_text:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter audit details.'
                }, status=400)
            
            # Truncate text if too long
            if len(audit_text) > 2000:
                audit_text = audit_text[:2000]
            
            # Create the prompt
            prompt = f'''
You are a sustainability auditor. Your job is to analyze the following sustainability practices provided by a company. Based on the provided details, provide actionable insights and data analysis. Highlight areas of improvement, potential cost-saving opportunities, and sustainability metrics.

The following is the company's sustainability audit data:

{audit_text}

Please provide actionable insights, suggestions for improvements, and overall sustainability performance analysis.
'''
            
            # Call OpenAI API
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return JsonResponse({
                    'success': False,
                    'message': 'OpenAI API key not configured.'
                }, status=500)
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful sustainability auditor."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            # Save to database if user is authenticated
            if request.user.is_authenticated:
                audit = GreenAudit.objects.create(
                    user=request.user,
                    audit_text=audit_text,
                    analysis_result=result
                )
            
            return JsonResponse({
                'success': True,
                'result': result
            })
            
        except Exception as e:
            print(f'Error during analysis: {e}')
            return JsonResponse({
                'success': False,
                'message': 'Failed to analyze the data. Please try again.'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)


@csrf_exempt
def extract_text_from_image(request):
    """API endpoint to extract text from uploaded electricity bill image using EasyOCR"""
    if request.method == 'POST':
        try:
            if 'image' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'message': 'No image uploaded.'
                }, status=400)
            
            image_file = request.FILES['image']
            
            # Save the image permanently
            file_path = default_storage.save(f'audit_images/{image_file.name}', image_file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Extract text using EasyOCR
            try:
                import easyocr
                import cv2
                import numpy as np
                from PIL import Image
                
                # Initialize EasyOCR reader (English)
                reader = easyocr.Reader(['en'])
                
                # Read the image
                result = reader.readtext(full_path)
                
                # Combine all detected text
                extracted_text = ' '.join([text[1] for text in result])
                
                # Extract electricity bill data
                bill_data = extract_bill_data(extracted_text)
                
                # Get AI analysis
                analysis = analyze_electricity_bill(extracted_text, bill_data)
                
                # Save to database
                audit = GreenAudit.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    audit_text=extracted_text,
                    image=file_path,
                    analysis_result=analysis,
                    bill_number=bill_data.get('bill_number'),
                    account_number=bill_data.get('account_number'),
                    billing_period=bill_data.get('billing_period'),
                    kwh_consumption=bill_data.get('kwh_consumption'),
                    total_amount=bill_data.get('total_amount'),
                    previous_reading=bill_data.get('previous_reading'),
                    current_reading=bill_data.get('current_reading'),
                    supply_charge=bill_data.get('supply_charge'),
                    energy_charge=bill_data.get('energy_charge'),
                )
                
                return JsonResponse({
                    'success': True,
                    'extracted_text': extracted_text,
                    'bill_data': bill_data,
                    'analysis': analysis,
                    'audit_id': audit.id
                })
                
            except Exception as e:
                print(f'OCR Error: {e}')
                import traceback
                traceback.print_exc()
                return JsonResponse({
                    'success': False,
                    'message': f'Failed to extract text from image: {str(e)}'
                }, status=500)
            
        except Exception as e:
            print(f'Error processing image: {e}')
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Failed to process image: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)


def extract_bill_data(text):
    """Extract specific data from Mauritius electricity bill text"""
    data = {}
    
    # Common patterns in Mauritius electricity bills
    patterns = {
        'kwh_consumption': r'(?:consumption|units|kwh)[:\s]*([0-9,]+\.?[0-9]*)',
        'total_amount': r'(?:total|amount due|payable)[:\s]*(?:rs|mur)?\s*([0-9,]+\.?[0-9]*)',
        'account_number': r'(?:account|acc)[:\s#]*([0-9A-Z-]+)',
        'bill_number': r'(?:bill|invoice)[:\s#]*([0-9A-Z-]+)',
        'previous_reading': r'(?:previous|prev)[:\s]*([0-9,]+)',
        'current_reading': r'(?:current|present)[:\s]*([0-9,]+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '')
            try:
                if key in ['kwh_consumption', 'total_amount', 'previous_reading', 'current_reading', 'supply_charge', 'energy_charge']:
                    data[key] = Decimal(value)
                else:
                    data[key] = value
            except (InvalidOperation, ValueError):
                pass
    
    return data


def analyze_electricity_bill(extracted_text, bill_data):
    """Analyze electricity bill using OpenAI with specific focus on Mauritius context"""
    try:
        kwh = bill_data.get('kwh_consumption', 'N/A')
        amount = bill_data.get('total_amount', 'N/A')
        
        prompt = f'''You are a certified energy auditor and sustainability expert for Mauritius. Analyze this electricity bill data and provide a professional, comprehensive green audit report in HTML format.

Extracted Bill Data:
- Monthly kWh Consumption: {kwh}
- Total Bill Amount: MUR {amount}
- Full Text: {extracted_text[:1500]}

IMPORTANT: Calculate all numbers accurately based on the actual consumption. Use these facts:
- Average Mauritius household: 250-350 kWh/month
- CEB residential rates (2024): Tier 1 (0-50 kWh): MUR 2.96/kWh, Tier 2 (51-300 kWh): MUR 4.17/kWh, Tier 3 (301-800 kWh): MUR 5.30/kWh
- Solar system cost: MUR 75,000-85,000 per kW installed
- Average daily sunshine: 5.5 hours in Mauritius
- CO2 factor: 0.79 kg per kWh (Mauritius grid)
- Solar panel efficiency: 350W panels, need ~3 panels per kW

Provide detailed analysis in HTML format:

<div class="analysis-section">
<h3>⚡ Energy Usage Assessment</h3>
<p><strong>Monthly Consumption:</strong> {kwh} kWh</p>
<p><strong>Daily Average:</strong> [Calculate: kwh/30] kWh/day</p>
<p><strong>Benchmark Comparison:</strong></p>
<ul>
<li>Your consumption: {kwh} kWh/month</li>
<li>Average Mauritian household: 300 kWh/month</li>
<li>Efficient household target: 180 kWh/month</li>
<li><strong>Status:</strong> [State if HIGH/MODERATE/LOW with percentage above/below average]</li>
</ul>
<p><strong>Peak Usage Analysis:</strong> Based on CEB billing tiers, approximately [calculate percentage] of your consumption falls in Tier [X], indicating [heavy/moderate/light] usage patterns.</p>
</div>

<div class="analysis-section">
<h3>💰 Cost Analysis</h3>
<p><strong>Current Bill Breakdown:</strong></p>
<ul>
<li>Total Amount: MUR {amount}</li>
<li>Average Cost per kWh: MUR [Calculate: amount/kwh rounded to 2 decimals]</li>
<li>Projected Annual Cost: MUR [Calculate: amount * 12]</li>
<li>Average Daily Cost: MUR [Calculate: amount/30 rounded to 2 decimals]</li>
</ul>
<p><strong>CEB Rate Comparison:</strong> Your effective rate of MUR [calculated rate]/kWh indicates [tier analysis]. Reducing consumption below 300 kWh could save approximately MUR [calculate potential savings] monthly.</p>
</div>

<div class="analysis-section">
<h3>☀️ Solar Energy Investment Analysis</h3>
<p><strong>Recommended System:</strong></p>
<ul>
<li><strong>System Size:</strong> [Calculate: kwh / (5.5 hours * 30 days * 0.85 efficiency), round to nearest 0.5] kW solar system</li>
<li><strong>Panel Configuration:</strong> [Calculate number of 350W panels needed] x 350W panels</li>
<li><strong>Investment Cost:</strong> MUR [Calculate: system_size * 80,000] (including installation)</li>
<li><strong>Monthly Production:</strong> ~[Calculate: system_size * 5.5 * 30 * 0.85] kWh</li>
<li><strong>Bill Reduction:</strong> [Calculate percentage] - Estimated MUR [calculate savings] per month</li>
<li><strong>Payback Period:</strong> [Calculate: investment / (monthly_savings * 12)] years</li>
<li><strong>25-Year Savings:</strong> MUR [Calculate long-term savings minus investment]</li>
</ul>
<p><strong>Net Metering Benefits:</strong> Excess energy sold to CEB at MUR 5/kWh. Estimated monthly surplus: [calculate if system produces more than consumption] kWh = MUR [calculate earnings].</p>
<p><strong>Government Support:</strong> 60% subsidy reduces cost to MUR [calculate after subsidy]. Some commercial banks offer green loans at 3.5-4.5% interest.</p>
</div>

<div class="analysis-section">
<h3>🌱 Practical Energy Efficiency Measures</h3>
<p><strong>High-Impact Actions:</strong></p>
<ul>
<li><strong>LED Conversion:</strong> Replace [estimate 15-20] bulbs. Investment: MUR 3,000-4,500. Savings: ~50 kWh/month (MUR 200-250)</li>
<li><strong>AC Optimization:</strong> Set to 24-25°C instead of 20°C. Potential savings: 15-20% on cooling costs (MUR [calculate based on estimated AC usage])</li>
<li><strong>Solar Water Heater:</strong> Replace electric geyser. Cost: MUR 25,000-35,000. Saves 100-150 kWh/month (MUR 400-600). Payback: 3-4 years</li>
<li><strong>Energy-Efficient Refrigerator:</strong> Modern inverter model saves 30-40 kWh/month (MUR 120-160)</li>
<li><strong>Standby Power Elimination:</strong> Use power strips. Saves 5-8% total consumption (MUR [calculate])</li>
</ul>
</div>

<div class="analysis-section">
<h3>🌍 Environmental Impact</h3>
<p><strong>Current Carbon Footprint:</strong></p>
<ul>
<li>Monthly CO2 Emissions: [Calculate: kwh * 0.79] kg CO2</li>
<li>Annual CO2 Emissions: [Calculate: kwh * 0.79 * 12] kg CO2</li>
<li>Equivalent to: [Calculate trees needed: annual_co2 / 21] trees needed to offset</li>
<li>Car comparison: Equivalent to driving [calculate: annual_co2 / 0.12] km annually</li>
</ul>
<p><strong>With Solar:</strong> Reduce emissions by [calculate percentage]%, offsetting [calculate] kg CO2 annually.</p>
</div>

<div class="analysis-section action-plan">
<h3>📋 Prioritized Action Plan</h3>
<ol>
<li><strong>Immediate (This Month):</strong> LED bulb replacement + AC settings optimization - Investment: MUR 4,000 | Monthly Savings: MUR [calculate 250-300]</li>
<li><strong>Short-term (3 months):</strong> Install smart power strips and standby eliminator - Investment: MUR 1,500 | Monthly Savings: MUR [calculate 80-120]</li>
<li><strong>Medium-term (6 months):</strong> Solar water heater installation - Investment: MUR 30,000 (after subsidy: MUR 12,000) | Monthly Savings: MUR [calculate 450-550]</li>
<li><strong>Long-term (12 months):</strong> Solar PV system [calculated size] kW - Investment: MUR [calculated with subsidy] | Monthly Savings: MUR [calculated]</li>
<li><strong>Ongoing:</strong> Energy monitoring and behavioral changes - Zero cost | Monthly Savings: MUR [calculate 100-150]</li>
</ol>
<p><strong>Total Implementation Cost:</strong> MUR [sum of all investments]</p>
<p><strong>Total Monthly Savings:</strong> MUR [sum of all savings] ([calculate percentage]% reduction)</p>
<p><strong>First Year Net Savings:</strong> MUR [annual savings - investments]</p>
<p><strong>5-Year Total Savings:</strong> MUR [5 year projection]</p>
</div>

<div class="analysis-section highlight-box">
<h3>💡 CEB Net Metering Program</h3>
<p><strong>How You Can Sell Energy:</strong></p>
<ul>
<li><strong>Current Regulation:</strong> CEB buys excess solar at MUR 5.00/kWh (July 2024 rate)</li>
<li><strong>Your Potential:</strong> With [calculated] kW system, estimated monthly surplus: [calculate] kWh worth MUR [calculate]</li>
<li><strong>Application Process:</strong> 4-6 weeks approval through CEB Green Energy Office</li>
<li><strong>Requirements:</strong> Bi-directional smart meter (provided by CEB), registered installer, compliance certificate</li>
<li><strong>Settlement:</strong> Annual net billing - credits roll over monthly, cash settlement yearly</li>
<li><strong>Return on Investment:</strong> With energy selling, payback improves to [calculate improved payback] years</li>
</ul>
</div>

Provide ALL calculations with actual numbers. Be precise and professional like a real energy audit report.'''
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "OpenAI API key not configured. Please add it to .env file."
        
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful energy efficiency expert specializing in Mauritius."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f'Analysis error: {e}')
        return f"Analysis failed: {str(e)}"