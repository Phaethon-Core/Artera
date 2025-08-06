from fastapi import HTTPException
import apps.user_service.models as user_models
from sqlalchemy.orm import joinedload


def register_user(payload, db):
    existing_email = db.query(user_models.User).filter(
        user_models.User.email == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_models.User(first_name=payload.first_name,
                            last_name=payload.last_name, email=payload.email)
    db.add(user)
    db.commit()
    return user


def get_all_users(db):
    users = db.query(user_models.User).all()
    return users


def get_user(user_id, db):
    user = db.query(user_models.User).filter(
        user_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_profile(user_id, db):
    profile = db.query(user_models.Profile).options(
        joinedload(user_models.Profile.user)).filter(user_models.Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


def create_or_update_user_profile(user_id, payload, db):
    user = db.query(user_models.User).filter(
        user_models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(user_models.Profile).filter(
        user_models.Profile.user_id == user_id
    ).first()

    if profile:
        # Update existing profile
        profile.bio = payload.bio
        profile.instagram_link = payload.instagram_link
        profile.x_link = payload.x_link
        profile.art_station_link = payload.art_station_link
    else:
        # Create new profile
        profile = user_models.Profile(
            user_id=user.id,
            bio=payload.bio,
            instagram_link=payload.instagram_link,
            x_link=payload.x_link,
            art_station_link=payload.art_station_link
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile
