"""
TruthGuard User Profile & Preferences Management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models import User, UserSettings
from backend.app.schemas import (
    UserResponse, ProfileUpdateRequest, PasswordChangeRequest,
    UserSettingsResponse, UserSettingsUpdateRequest
)
from backend.app.auth.security import hash_password, verify_password
from backend.app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])
settings_router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=UserResponse)
def update_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.full_name is not None:
        current_user.full_name = req.full_name.strip()
    if req.username is not None:
        existing = db.query(User).filter(User.username == req.username.strip(), User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username is already in use.")
        current_user.username = req.username.strip()
    if req.profile_image is not None:
        current_user.profile_image = req.profile_image

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/password")
def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password does not match.")
    current_user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "Password changed successfully."}


@router.delete("")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes the current user account and all associated verification records."""
    db.delete(current_user)
    db.commit()
    return {"message": "Account and all associated records permanently deleted."}


# --- Settings Routes ---
@settings_router.get("", response_model=UserSettingsResponse)
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@settings_router.put("", response_model=UserSettingsResponse)
def update_user_settings(
    req: UserSettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    if req.theme is not None:
        settings.theme = req.theme
    if req.language is not None:
        settings.language = req.language
    if req.default_verification_mode is not None:
        settings.default_verification_mode = req.default_verification_mode
    if req.default_correction_mode is not None:
        settings.default_correction_mode = req.default_correction_mode
    if req.notification_preferences is not None:
        settings.notification_preferences = req.notification_preferences

    db.commit()
    db.refresh(settings)
    return settings
