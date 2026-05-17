import uuid
import bcrypt
import mysql.connector
from fastapi import HTTPException
from database import get_db_connection

from services.otp_service import generate_and_dispatch_otp

async def register_new_user(username: str, email: str, password: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT email FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email is already registered")
            
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        new_user_id = str(uuid.uuid4())
        
        insert_user_query = """
            INSERT INTO Users (user_id, username, email, password_hash, is_email_verified)
            VALUES (%s, %s, %s, %s, FALSE)
        """
        cursor.execute(insert_user_query, (new_user_id, username, email, hashed_password.decode('utf-8')))
        conn.commit()
        
        await generate_and_dispatch_otp(new_user_id, email)
        
        return {
            "status": "pending_verification",
            "user_id": new_user_id,
            "message": "Account created! Please check your email for your 6-digit verification code."
        }

    except mysql.connector.Error as err:
        conn.rollback() 
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()