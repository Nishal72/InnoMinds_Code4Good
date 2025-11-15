from django.conf import settings

try:
    from twilio.rest import Client
except ImportError:
    Client = None


def send_encrypted_sms(message: str, to_number: str):
    """
    Send encrypted SMS via Twilio.
    Returns (success: bool, info: str)
    """
    # Basic safety checks
    if Client is None:
        return False, "Twilio client not installed. Run 'pip install twilio'."

    sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_num = getattr(settings, "TWILIO_FROM_NUMBER", None)

    if not (sid and token and from_num):
        return False, "Twilio settings not configured in settings.py / .env."

    if not to_number:
        return False, "No destination phone number provided."

    try:
        client = Client(sid, token)
        msg = client.messages.create(
            body=message,
            from_=from_num,
            to=to_number,
        )
        return True, msg.sid
    except Exception as e:
        return False, str(e)
