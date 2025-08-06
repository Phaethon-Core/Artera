from fastapi import APIRouter, HTTPException, Depends, status
import apps.user_service.services as user_service
import apps.user_service.schemas as user_schemas
from base.db import get_db
from sqlalchemy.orm import Session
import uuid

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/")
def health():
    return {"status": "ok", "router": "user api"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: user_schemas.RegisterUser, db: Session = Depends(get_db)):
    try:
        res = user_service.register_user(data, db)
        return {"message": f"User registered successfully."}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"{e.detail}")


@router.get("/all")
def get_all_users(db: Session = Depends(get_db)):
    try:
        users = user_service.get_all_users(db)
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"{e.detail}")


@router.get("/{user_id}")
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        user = user_service.get_user(user_id, db)
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"{e.detail}")


@router.get("/profile/{user_id}")
def get_user_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        user = user_service.get_user_profile(user_id, db)
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"{e.detail}")


@router.post('/profile/{user_id}', status_code=status.HTTP_201_CREATED)
def create_user_profile(user_id: uuid.UUID, payload: user_schemas.ProfilePayload, db: Session = Depends(get_db)):
    try:
        profile = user_service.create_user_profile(user_id, payload, db)
        return {"message": "Profile created successfully."}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"{e.detail}")
