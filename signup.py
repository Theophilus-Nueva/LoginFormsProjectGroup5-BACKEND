import uuid
import hashlib
import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector

# Import your shared database connection
from database import get_db_connection

# Initialize the router
router = APIRouter()

# --- PYDANTIC MODEL ---
class UserSignup(BaseModel):
    username: str
    email: str
    password: str

# --- SIGNUP ROUTE ---
@router.post("/signup")
def create_user(user: UserSignup):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Check if the email already exists to prevent duplicates
        cursor.execute("SELECT email FROM Users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email is already registered")
            
        # 2. Prepare the secure user data
        new_user_id = str(uuid.uuid4())
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        
        # 3. Insert the new user into the database
        insert_user_query = """
            INSERT INTO Users (user_id, username, email, password_hash, is_email_verified)
            VALUES (%s, %s, %s, %s, FALSE)
        """
        cursor.execute(insert_user_query, (new_user_id, user.username, user.email, hashed_password))
        
        # 4. Generate a mathematically secure Email Verification Token
        verification_token = secrets.token_urlsafe(32)
        
        # 5. Save the token to the Verification_Tokens table (Valid for 24 hours)
        insert_token_query = """
            INSERT INTO Verification_Tokens (token, user_id, expires_at)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 1 DAY))
        """
        cursor.execute(insert_token_query, (verification_token, new_user_id))
        
        # 6. Save all changes to the database
        conn.commit()
        
        return {
            "status": "success",
            "message": "User created successfully! Please check your email to verify your account.",
            "mock_token_for_testing": verification_token 
        }

    except mysql.connector.Error as err:
        conn.rollback() # Undo the transaction if something breaks!
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()