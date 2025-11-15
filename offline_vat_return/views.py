from django.shortcuts import render, redirect
from .forms import VATReturnForm
from .utils import encrypt_message, decrypt_message
from .sms import send_encrypted_sms


def vat_form(request):
    if request.method == "POST":
        form = VATReturnForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            message = f"""
Business Name: {obj.business_name}
Business ID: {obj.business_id}
VAT Collected: {obj.vat_collected}
VAT Paid: {obj.vat_paid}
Reporting Period: {obj.reporting_period}
"""

            encrypted = encrypt_message(message)
            obj.encrypted_message = encrypted
            obj.save()

            # 🔐 Try sending encrypted SMS
            sms_sent = False
            sms_sid = None
            sms_error = None

            sms_sent, info = send_encrypted_sms(encrypted, obj.phone_number)
            if sms_sent:
                sms_sid = info
            else:
                sms_error = info

            return render(request, "offline_vat_return/submit_success.html", {
                "encrypted": encrypted,
                "sms_sent": sms_sent,
                "sms_sid": sms_sid,
                "sms_error": sms_error,
                "phone_number": obj.phone_number,
            })

    else:
        form = VATReturnForm()

    return render(request, "offline_vat_return/vat_form.html", {
        "form": form
    })

def decrypt_tool(request):
    output = None
    if request.method == "POST":
        ciphertext = request.POST.get("ciphertext")
        try:
            output = decrypt_message(ciphertext)
        except Exception as e:
            output = f"Error: {str(e)}"

    return render(request, "offline_vat_return/decrypt_tool.html", {
        "output": output
    })
