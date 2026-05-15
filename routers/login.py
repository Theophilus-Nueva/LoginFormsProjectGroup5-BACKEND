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

# --- PYDANTIC MODELS ---
class UserLogin(BaseModel):
    email: str
    password: str

class VerifyOTP(BaseModel):
    user_id: str
    code: str

# --- LOGIN ROUTE ---
@router.post("/login")
def login_user(user: UserLogin):
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
            
        # ---------------------------------------------------------
        # THIS IS WHAT CHANGED: No more mock_email_otp = "456"
        # ---------------------------------------------------------
        
        # 1. Generate a true cryptographically secure 6-digit code
        live_otp = ''.join(secrets.choice('0123456789') for i in range(6))
        
        # 2. Save the REAL code to the database
        insert_otp_query = """
            INSERT INTO `2_factor_authentication_code` (user_id, code, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE))
        """
        cursor.execute(insert_otp_query, (db_user["user_id"], live_otp))
        conn.commit()
        
        # 3. Actually send the email using our new utils.py function!
        email_sent = send_email_otp(user.email, live_otp)
        
        if not email_sent:
            # Tell the frontend if Google blocked the email for some reason
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

# (Your existing @router.post("/verify-otp") function goes down here!)