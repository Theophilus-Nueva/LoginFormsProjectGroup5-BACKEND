# services/audit.py
from database import get_db_connection
from fastapi import Request

def log_auth_event(email: str, event_type: str, user_id: str = None, request: Request = None):
    """Silently logs authentication attempts to the database with real client IP tracking."""
    ip_address = "127.0.0.1"
    
    if request and request.client:
        ip_address = request.client.host
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Authentication_Logs (user_id, email_attempted, ip_address, event_type)
            VALUES (%s, %s, %s, %s)
        """, (user_id, email, ip_address, event_type))
        conn.commit()
    except Exception as e:
        print(f"Audit Log Error: {e}")
    finally:
        cursor.close()
        conn.close()