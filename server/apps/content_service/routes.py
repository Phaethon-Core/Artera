from fastapi import APIRouter

router = APIRouter(prefix="/api/content", tags=["Content"])


@router.get("/health")
def health():
    return {"status": "ok"}
