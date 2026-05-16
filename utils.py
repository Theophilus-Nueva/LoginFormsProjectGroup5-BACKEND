# utils.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

import requests

load_dotenv()

def send_email_otp(recipient_email: str, otp_code: str):
    api_key = os.getenv("BREVO_API_KEY")
    
    sender_email = "your.group5.email@gmail.com" 
    
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
        "to": [
            {
                "email": recipient_email
            }
        ],
        "subject": "Group 5 Project - Your Security Code",
        "htmlContent": f"<html><body><h3>Hello!</h3><p>Your Multi-Factor Authentication code is: <strong style='font-size: 24px;'>{otp_code}</strong></p><p>This code will expire in 10 minutes.</p><p>Securely,<br>Group 5 Security</p></body></html>"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print("✅ SUCCESS! Brevo sent the email.")
            return True
        else:
            print(f"❌ FAILED! Brevo error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL HTTP ERROR: {e}")
        return False