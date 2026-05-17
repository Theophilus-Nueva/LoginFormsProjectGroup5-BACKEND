from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from services.verify_otp import validate_and_consume_otp

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class VerifyOTPRequest(BaseModel):
    user_id: str 
    otp_code: str

@router.post("/verify-otp")
async def verify_otp(request_data: VerifyOTPRequest, request: Request):
    success_response = validate_and_consume_otp(
        user_id=request_data.user_id,
        otp_code=request_data.otp_code
        request=request
    )
    
    return success_response