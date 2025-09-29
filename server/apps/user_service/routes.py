from fastapi import APIRouter, HTTPException, Depends, status, Request
import apps.user_service.services as user_service
import apps.user_service.schemas as user_schemas
from base.db import get_db
from sqlalchemy.orm import Session
import uuid
from base.middleware import require_roles

router = APIRouter(prefix="/api/user", tags=["User"])


@router.get("/")
def health():
    return {"status": "ok", "router": "user api"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: user_schemas.RegisterUser, db: Session = Depends(get_db)):
    try:
        user_service.register_user(data, db)
        return {"message": f"User registered successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.get("/all")
def get_all_users(db: Session = Depends(get_db)):
    try:
        users = user_service.get_all_users(db)
        return {"users": users}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.get("/{user_id}")
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db), _: dict = Depends(require_roles(["admin", "user"]))):
    try:
        user = user_service.get_user(user_id, db)
        return {"user": user}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.get("/profile/{user_id}")
def get_user_profile(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles(["admin", "user"]))
):
    try:
        # req_user = Request.user
        # print(req_user)
        user = user_service.get_user_profile(user_id, db)
        return {"user": user}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.post('/profile/{user_id}', status_code=status.HTTP_201_CREATED)
def create_user_profile(
        user_id: uuid.UUID,
        payload: user_schemas.ProfilePayload,
        db: Session = Depends(get_db),
        _: dict = Depends(require_roles(["user"]))):
    try:
        req_user = Request.user["sub"]
        user_service.create_or_update_user_profile(
            user_id, req_user, payload, db)
        return {"message": "Profile created successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")
