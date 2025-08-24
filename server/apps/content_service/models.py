from base.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UUID, Text, DateTime, Boolean
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship


class Content(Base):
    __tablename__ = 'contents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    comments = relationship(
        "Comment", back_populates="content", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey(
        'comments.id'), nullable=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey(
        'contents.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

    content = relationship("Content", back_populates="comments")
    thread = relationship("Comment", remote_side=[
                          id], back_populates="replies")
    replies = relationship(
        "Comment", back_populates="thread", cascade="all, delete-orphan")
