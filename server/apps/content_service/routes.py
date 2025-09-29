from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile
import apps.content_service.services as content_services
import apps.content_service.schemas as content_schemas
from sqlalchemy.orm import Session
from base.db import get_db
from base.middleware import require_roles

router = APIRouter(prefix="/api/content", tags=["Content"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/")
def create_content(data: content_schemas.ContentCreate, content: File = UploadFile(), db: Session = Depends(get_db), _: dict = Depends(require_roles("user"))):
    try:
        user = Request.user["sub"]
        content = content_services.create_new_content(data, user, db)
        return content
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.get("/")
def get_contents():
    pass


@router.get("/{content_id}")
def get_content_by_id():
    pass
