# email_service.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def send_email_otp(recipient_email: str, otp_code: str) -> bool:
    raw_api_key = os.getenv("BREVO_API_KEY", "")
    api_key = raw_api_key.replace('"', '').replace("'", "").strip()
    sender_email = os.getenv("SENDER_EMAIL", "loginformsprojectgroup5@gmail.com").strip()
    
    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {
            "name": "Group 5 Security",
            "email": sender_email
        },
        "to": [{"email": recipient_email}],
        "subject": "Group 5 Project - Your Security Code",
        "htmlContent": f"<html><body><h3>Hello!</h3><p>Your Multi-Factor Authentication code is: <strong style='font-size: 24px;'>{otp_code}</strong></p></body></html>"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 201
    except Exception:
        return False