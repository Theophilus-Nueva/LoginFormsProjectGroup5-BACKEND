import hashlib
import secrets # <-- NEW: Needed for real random numbers
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector

# Import your shared database connection
from database import get_db_connection

# <-- NEW: Import your digital postman from your toolbox
from utils import send_email_otp 

# Initialize the router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class UserLogin(BaseModel):
    email: str
    password: str

class VerifyOTP(BaseModel):
    user_id: str
    code: str

@router.post("/login")
async def login_user(user: UserLogin):
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
        
        # 4. Success Response
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
