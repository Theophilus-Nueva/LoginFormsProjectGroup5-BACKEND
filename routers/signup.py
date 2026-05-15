import uuid
import hashlib
import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector

# Import your shared database connection
from database import get_db_connection

router = APIRouter(prefix="/api/auth", tags=["Signup"])

class UserSignup(BaseModel):
    username: str
    email: str
    password: str

@router.post("/signup")
def create_user(user: UserSignup):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT email FROM Users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email is already registered")
            
        new_user_id = str(uuid.uuid4())
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        
        insert_user_query = """
            INSERT INTO Users (user_id, username, email, password_hash, is_email_verified)
            VALUES (%s, %s, %s, %s, FALSE)
        """
        cursor.execute(insert_user_query, (new_user_id, user.username, user.email, hashed_password))
        
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