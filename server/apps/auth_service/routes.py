from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from base.utils import otp_rate_limit, generate_otp, hash_otp, send_otp_email
from apps.user_service.models import User
from datetime import datetime, timedelta, timezone
from base.db import get_db
from sqlalchemy.orm import Session
from redis import Redis
from base.redis import get_redis_client
import json

router = APIRouter(prefix="/api", tags=["Auth"])

timestamps = {}
max_requests = 3
request_window = 60


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
        "otp": hashed_otp,
        "email": email,
        "expires_at": expires_at.isoformat()
    }

    redis.setex(f"otp:{email}", otp_expiry*60, json.dumps(otp_data))

    background_tasks.add_task(send_otp_email, otp_data)

    return {"message": "OTP sent successfully"}
