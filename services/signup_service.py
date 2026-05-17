import uuid
import secrets
import bcrypt
import mysql.connector
from fastapi import HTTPException
from database import get_db_connection

def register_new_user(username: str, email: str, password: str) -> dict:
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
        
        verification_token = secrets.token_urlsafe(32)
        insert_token_query = """
            INSERT INTO Verification_Tokens (token, user_id, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 1 DAY))
        """
        cursor.execute(insert_token_query, (verification_token, new_user_id))
        
        conn.commit()
        
        return {
            "status": "success",
            "message": "User created successfully! Please check your email to verify your account.",
            "mock_token_for_testing": verification_token 
        }

    except mysql.connector.Error as err:
        conn.rollback() 
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()