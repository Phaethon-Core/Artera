from pydantic import BaseModel
from typing import Optional


class ContentCreate(BaseModel):
    title: str
    description: Optional[str] = None


class CommentThread(BaseModel):
    comment: str
    thread_id: Optional[str] = None
    content_id: str
