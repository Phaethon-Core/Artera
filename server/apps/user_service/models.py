from base.db import Base
from sqlalchemy import Column, String, ForeignKey, UUID, DateTime, Text
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(String, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(
        timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(
        timezone.utc), nullable=False)
    role = Column(String, default="user", nullable=False)
    profile = relationship("Profile", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        'users.id'), nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String, nullable=True)
    cover_picture = Column(String, nullable=True)
    instagram_link = Column(String, nullable=True)
    x_link = Column(String, nullable=True)
    art_station_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(
        timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(
        timezone.utc), nullable=False)

    user = relationship("User", back_populates="profile")
