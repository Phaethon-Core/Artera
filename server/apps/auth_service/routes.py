from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from base.utils import otp_rate_limit, generate_otp, hash_otp, send_otp_email
from apps.user_service.models import User
from apps.auth_service.schemas import OtpVerifyRequest
from datetime import datetime, timedelta, timezone
from base.db import get_db
from base.middleware import create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from redis import Redis
from base.redis import get_redis_client
import json
import os

router = APIRouter(prefix="/api", tags=["Auth"])

timestamps = {}
max_requests = 3
request_window = 60

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


@router.post("/login")
async def login(email: str, background_tasks: BackgroundTasks, redis: Redis = Depends(get_redis_client), db: Session = Depends(get_db)):
    otp_rate_limit(email, timestamps, max_requests, request_window)

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    otp = generate_otp()
    hashed_otp = hash_otp(otp)

    otp_expiry = 10
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=otp_expiry)

    otp_data = {
        "plain": otp,
        "otp": hashed_otp,
        "email": email,
        "expires_at": expires_at.isoformat()
    }

    redis.setex(f"otp:{email}", otp_expiry*60, json.dumps(otp_data))

    background_tasks.add_task(send_otp_email, otp_data)

    return {"message": "OTP sent successfully"}


@router.post("/verify")
async def verify_otp(
    email: str,
    otp: str,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client)
):
    otp_data = redis.get(f"otp:{email}")

    if not otp_data:
        raise HTTPException(status_code=404, detail="OTP not found")

    otp_data = json.loads(otp_data)

    if otp_data["otp"] != hash_otp(otp):
        raise HTTPException(status_code=401, detail="Invalid OTP")

    if datetime.now(timezone.utc) > datetime.fromisoformat(otp_data["expires_at"]):
        raise HTTPException(status_code=401, detail="OTP expired")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "role": user.role})
    refresh_token = create_refresh_token(
        {"sub": str(user.id), "email": user.email, "role": user.role})

    redis.setex(f"refresh_token:{user.id}",
                REFRESH_TOKEN_EXPIRE_DAYS * 86400, refresh_token)

    redis.delete(f"otp:{email}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
