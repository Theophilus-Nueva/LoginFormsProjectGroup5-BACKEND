from fastapi import APIRouter
from pydantic import BaseModel

from services.verify_recaptcha import verify_recaptcha
from services.verify_user_credentials import verify_user_credentials
from services.otp_service import generate_and_dispatch_otp

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class UserLogin(BaseModel):
    email: str
    password: str
    captcha_token: str 

@router.post("/login")
async def login_user(user: UserLogin):
    
    await verify_recaptcha(user.captcha_token)
    
    db_user = verify_user_credentials(user.email, user.password)
    
    success_response = await generate_and_dispatch_otp(db_user["user_id"], user.email)
    
    return success_response