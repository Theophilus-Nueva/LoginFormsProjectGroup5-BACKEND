import os
import requests

# NOTICE: load_dotenv() is COMPLETELY REMOVED. 
# Railway natively injects variables into the OS. We do not need dotenv in production.

def send_email_otp(recipient_email: str, otp_code: str) -> bool:
    # os.environ.get forces Python to look at the Railway OS directly
    api_key = os.environ.get("BREVO_API_KEY", "").strip()
    sender_email = os.environ.get("SENDER_EMAIL", "loginformsprojectgroup5@gmail.com").strip()
    
    # EXTREME DEBUGGING: Let's see exactly what the server sees
    print("\n--- SERVER OS VARIABLE CHECK ---")
    if not api_key:
        print("❌ FATAL: API Key is completely blank. Railway is hiding it.")
    else:
        print(f"✅ API Key found! Length: {len(api_key)} characters (Should be around 74)")
    print("--------------------------------\n")
    
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
        
        if response.status_code == 201:
            print(f"✅ SUCCESS: Brevo delivered the email to {recipient_email}!")
            return True
        else:
            print(f"❌ FAIL: Brevo rejected it. Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False