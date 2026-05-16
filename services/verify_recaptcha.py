import os
import httpx

async def verify_recaptcha(token: str) -> bool:
    """
    Sends the frontend reCAPTCHA token to Google's API.
    Returns True if the user is verified as a human, False otherwise.
    """
    secret_key = os.getenv("RECAPTCHA_SECRET")
    
    if not secret_key:
        print("SECURITY WARNING: RECAPTCHA_SECRET environment variable is completely missing!")
        return False

    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(verify_url, data={
                "secret": secret_key,
                "response": token
            })
            result = response.json()
            return result.get("success", False)
            
    except Exception as e:
        print(f"reCAPTCHA Connection/API Error: {str(e)}")
        return False