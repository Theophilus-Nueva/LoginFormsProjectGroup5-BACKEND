import os
import secrets
import httpx
import mysql.connector
from fastapi import HTTPException
from dotenv import load_dotenv
from database import get_db_connection

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
URL = "https://api.brevo.com/v3/smtp/email"

async def send_email_otp(recipient_email: str, otp_code: str) -> bool:
    """Sends the actual HTTP request to Brevo."""
    if not BREVO_API_KEY or not SENDER_EMAIL:
        return False
        
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"name": "Group 5 Security", "email": SENDER_EMAIL},
        "to": [{"email": recipient_email}],
        "subject": "Group 5 Project - Your Security Code",
        "htmlContent": f"<html><body><h3>Hello!</h3><p>Your Multi-Factor Authentication code is: <strong style='font-size: 24px;'>{otp_code}</strong></p></body></html>"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(URL, json=payload, headers=headers)
        return response.status_code in [200, 201, 202]
    except Exception:
        return False


async def generate_and_dispatch_otp(user_id: str, email: str) -> dict:
    """Generates an OTP, saves it to the DB, emails the user, and returns the React payload."""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        live_otp = ''.join(secrets.choice('0123456789') for i in range(6))
        
        insert_otp_query = """
            INSERT INTO `2_factor_authentication_code` (user_id, code, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE))
        """
        cursor.execute(insert_otp_query, (user_id, live_otp))
        conn.commit()
        
        email_sent = await send_email_otp(email, live_otp)
        
        if not email_sent:
            raise HTTPException(status_code=500, detail="Failed to send verification email. Try again later.")
        
        return {
            "status": "mfa_required", 
            "user_id": user_id,
            "message": f"Success! A 6-digit code has been sent to {email}."
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()