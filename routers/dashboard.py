from fastapi import APIRouter, Depends, HTTPException
from services.security import verify_token
from database import get_db_connection
import mysql.connector

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/users")
async def get_all_users(user_id: str = Depends(verify_token)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # DO NOT select password_hash for security reasons!
        cursor.execute("""
            SELECT user_id, username, email, is_email_verified, 
                   failed_login_attempts, account_locked_until, created_at 
            FROM Users
        """)
        users = cursor.fetchall()
        return {"users": users}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error loading users")
    finally:
        cursor.close()
        conn.close()

@router.get("/logs")
async def get_all_logs(user_id: str = Depends(verify_token)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Authentication_Logs ORDER BY attempted_at DESC LIMIT 100")
        logs = cursor.fetchall()
        return {"logs": logs}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error loading logs")
    finally:
        cursor.close()
        conn.close()

@router.get("/tokens")
async def get_all_tokens(user_id: str = Depends(verify_token)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Verification_Tokens ORDER BY created_at DESC")
        tokens = cursor.fetchall()
        return {"tokens": tokens}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error loading tokens")
    finally:
        cursor.close()
        conn.close()

@router.get("/sessions")
async def get_all_sessions(user_id: str = Depends(verify_token)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Sessions ORDER BY created_at DESC")
        sessions = cursor.fetchall()
        return {"sessions": sessions}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error loading sessions")
    finally:
        cursor.close()
        conn.close()

@router.get("/mfa")
async def get_all_mfa_codes(user_id: str = Depends(verify_token)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM `2_factor_authentication_code` ORDER BY created_at DESC")
        mfa = cursor.fetchall()
        return {"mfa": mfa}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database error loading MFA codes")
    finally:
        cursor.close()
        conn.close()