import uuid
from fastapi import Request, Depends, HTTPException, status, Header
from typing import List
from sqlalchemy.orm import Session
from functools import wraps
from fastapi import Request, HTTPException, status, Depends
import hashlib
import os
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from typing import Optional
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from apps.user_service.models import User
from base.db import get_db
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")  # keep safe in env vars
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(
        timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(
        timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_and_verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if "exp" in payload:
            if datetime.now(timezone.utc).timestamp() > payload["exp"]:
                raise ExpiredSignatureError("Token has expired")

        return payload

    except ExpiredSignatureError:
        print("❌ Token expired")
        return None
    except InvalidTokenError:
        print("❌ Invalid token")
        return None


def decode_access_token(token: str):
    try:
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        db_gen = get_db()
        db = next(db_gen)
        user = db.query(User).filter(User.id ==
                                     payload.get("sub")).first()
        if not user:
            raise HTTPException(status_code=404, detail="Invalid token")
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")

    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def hash_otp_value(otp: str):
    return hashlib.sha256(otp.encode()).hexdigest()


def require_roles(required_roles: List[str]):
    def dependency(authorization: str = Header(..., alias="authorization")):
        payload = decode_access_token(authorization)
        Request.user = payload
        try:
            user_role = payload.get("role")
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Operation restricted to roles: {', '.join(required_roles)}"
                )
        except HTTPException as e:
            raise e
        return payload
    return dependency
