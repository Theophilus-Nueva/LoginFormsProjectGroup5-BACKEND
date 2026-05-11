import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector

# Import your shared database connection!
from database import get_db_connection

# Initialize the router
router = APIRouter()

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
            
        # Mock OTP Generation
        mock_email_otp = "456"
        active_otp = mock_email_otp 
        
        insert_otp_query = """
            INSERT INTO `2_factor_authentication_code` (user_id, code, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE))
        """
        cursor.execute(insert_otp_query, (db_user["user_id"], active_otp))
        conn.commit()
        
        return {
            "status": "mfa_required", 
            "user_id": db_user["user_id"],
            "message": "Please check your email/phone for the OTP."
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()