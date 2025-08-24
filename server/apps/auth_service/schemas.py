from pydantic import BaseModel


class OtpVerifyRequest(BaseModel):
    email: str
    otp: str
