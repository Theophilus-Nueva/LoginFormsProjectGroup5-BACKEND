from fastapi import APIRouter
from pydantic import BaseModel

from services.verify_recaptcha import verify_recaptcha
from services.signup_service import register_new_user

router = APIRouter(prefix="/api/auth", tags=["Signup"])

class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    captcha_token: str 

@router.post("/signup")
async def create_user(user: UserSignup):
    
    await verify_recaptcha(user.captcha_token)
    
    success_response = await register_new_user(user.username, user.email, user.password)
    
    return success_response