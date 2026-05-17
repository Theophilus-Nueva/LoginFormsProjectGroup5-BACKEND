import mysql.connector
from fastapi import HTTPException
from database import get_db_connection

def validate_and_consume_otp(user_id: str, otp_code: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        verify_query = """
            SELECT * FROM `2_factor_authentication_code` 
            WHERE user_id = %s AND code = %s AND expires_at > NOW()
        """
        cursor.execute(verify_query, (user_id, otp_code))
        valid_otp = cursor.fetchone()
        
        if not valid_otp:
             raise HTTPException(status_code=401, detail="Invalid or expired verification code.")
             
        delete_query = "DELETE FROM `2_factor_authentication_code` WHERE user_id = %s"
        cursor.execute(delete_query, (user_id,))
        
        activate_query = "UPDATE Users SET is_email_verified = TRUE WHERE user_id = %s"
        cursor.execute(activate_query, (user_id,))
        
        conn.commit()
        
        return {
            "status": "success", 
            "message": "Authentication complete! Logging you in..."
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Internal server database error.")
    finally:
        cursor.close()
        conn.close()