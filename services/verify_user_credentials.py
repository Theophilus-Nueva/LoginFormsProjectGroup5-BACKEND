import bcrypt
import mysql.connector
from fastapi import HTTPException
from database import get_db_connection

def get_user_if_exists(email: str, cursor) -> dict:
    cursor.execute("SELECT user_id, password_hash FROM Users WHERE email = %s", (email,))
    return cursor.fetchone()

def is_password_correct(raw_password: str, stored_hash_str: str) -> bool:
    raw_attempt = raw_password.encode('utf-8')
    stored_hash = stored_hash_str.encode('utf-8')
    return bcrypt.checkpw(raw_attempt, stored_hash)


def verify_user_credentials(email: str, password: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        db_user = get_user_if_exists(email, cursor)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        if not is_password_correct(password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        return db_user

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()