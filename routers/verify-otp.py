# Add this data model at the top of your file with the others
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

from database import get_db_connection

class VerifyOTPRequest(BaseModel):
    user_id: int
    otp_code: str

@router.post("/verify-otp")
async def verify_otp(request_data: VerifyOTPRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        verify_query = """
            SELECT * FROM `2_factor_authentication_code` 
            WHERE user_id = %s AND code = %s AND expires_at > NOW()
        """
        cursor.execute(verify_query, (request_data.user_id, request_data.otp_code))
        valid_otp = cursor.fetchone()
        
        if not valid_otp:
             raise HTTPException(status_code=401, detail="Invalid or expired verification code.")
             
        delete_query = "DELETE FROM `2_factor_authentication_code` WHERE user_id = %s"
        cursor.execute(delete_query, (request_data.user_id,))
        conn.commit()
        
        return {
            "status": "success", 
            "message": "Authentication complete! Logging you in..."
        }

    except Exception as e:
        print(f"OTP VERIFY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
        
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()