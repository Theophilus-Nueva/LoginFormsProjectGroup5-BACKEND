from fastapi import APIRouter, Depends
from services.security import verify_token
from database import get_db_connection

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/my-data")
async def get_secure_dashboard_data(user_id: str = Depends(verify_token)):
    """
    This route is IMPOSSIBLE to access without a valid JWT.
    If the token is valid, verify_token automatically extracts the user_id and passes it here!
    """
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Now you can safely fetch data belonging ONLY to this specific user
        cursor.execute("SELECT username, email FROM Users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        return {
            "message": f"Welcome to the vault, {user_data['username']}!",
            "secret_data": "Here is the highly sensitive data for your eyes only."
        }
        
    finally:
        cursor.close()
        conn.close()