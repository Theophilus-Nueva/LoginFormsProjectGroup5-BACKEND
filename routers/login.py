import hashlib
import secrets 
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector

from database import get_db_connection
from services.email_service import send_email_otp 
from services.verify_recaptcha import verify_recaptcha

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# 1. Fixed: Model now expects the captcha token from React
class UserLogin(BaseModel):
    email: str
    password: str
    captcha_token: str 

class VerifyOTP(BaseModel):
    user_id: str
    code: str

@router.post("/login")
async def login_user(user: UserLogin):
    # 2. Fixed: Verify status BEFORE touching or opening database resources
    is_human = await verify_recaptcha(user.captcha_token)
    if not is_human:
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed.")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT user_id, password_hash FROM Users WHERE email = %s", (user.email,))
        db_user = cursor.fetchone()
        
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        hashed_attempt = hashlib.sha256(user.password.encode()).hexdigest()
        
        if hashed_attempt != db_user["password_hash"]:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        live_otp = ''.join(secrets.choice('0123456789') for i in range(6))
        
        insert_otp_query = """
            INSERT INTO `2_factor_authentication_code` (user_id, code, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE))
        """
        cursor.execute(insert_otp_query, (db_user["user_id"], live_otp))
        conn.commit()
        
        email_sent = await send_email_otp(user.email, live_otp)
        
        if not email_sent:
            raise HTTPException(status_code=500, detail="Failed to send verification email. Try again later.")
        
        return {
            "status": "mfa_required", 
            "user_id": db_user["user_id"],
            "message": f"Success! A 6-digit code has been sent to {user.email}."
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()