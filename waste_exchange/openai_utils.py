from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_quote_email(user_name, user_email, message_body, business):
    prompt = f"""
    Write a professional quotation request email.

    The sender is a potential customer requesting a price or quotation from this business.

    Sender name: {user_name}
    Sender email: {user_email}

    Business receiving the request:
    - Name: {business.name}
    - Category: {business.category.name if business.category else "Not specified"}

    Main user request:
    {message_body}

    Format the email clearly and politely.
    Tone: respectful, concise, customer-like.
    Start with a greeting ("Good day"/"Hello"), address the business by name, explain the need, 
    include the sender's contact info, and end with thanks.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional email writing assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    return response.choices[0].message.content
