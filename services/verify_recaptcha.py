import os
import httpx
from fastapi import HTTPException

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
SECRET_KEY = os.getenv("RECAPTCHA_SECRET")

async def is_recaptcha_verified(token: str) -> bool:
    if not SECRET_KEY:
        print("SECURITY WARNING: RECAPTCHA_SECRET environment variable is completely missing!")
        return False
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(VERIFY_URL, data={
                "secret": SECRET_KEY,
                "response": token
            })
            result = response.json()
            return result.get("success", False)
    except Exception as e:
        print(f"reCAPTCHA Connection/API Error: {str(e)}")
        return False
    
async def verify_recaptcha(token: str) -> None:
    if not await is_recaptcha_verified(token):
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed.")
    