# services/audit.py
from database import get_db_connection

def log_auth_event(email: str, event_type: str, user_id: str = None, ip_address: str = "127.0.0.1"):
    """Silently logs authentication attempts to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Authentication_Logs (user_id, email_attempted, ip_address, event_type)
            VALUES (%s, %s, %s, %s)
        """, (user_id, email, ip_address, event_type))
        conn.commit()
    except Exception as e:
        print(f"Audit Log Error: {e}") # Fails silently so it doesn't break the user's login!
    finally:
        cursor.close()
        conn.close()