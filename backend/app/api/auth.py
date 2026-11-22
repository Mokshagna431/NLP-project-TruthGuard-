"""
TruthGuard Authentication Routes: Register, Login, Logout, Profile Check, Password Reset
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.connection import get_db
from backend.app.models import User, UserSettings, VerificationJob, Claim
from backend.app.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse,
    UserResponse, ForgotPasswordRequest, ResetPasswordRequest
)
from backend.app.auth.security import hash_password, verify_password, create_access_token
from backend.app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user account with hashed password and default settings."""
    # Check if email or username already exists
    if db.query(User).filter(User.email == req.email.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken. Please choose another."
        )

    # First registered user can be admin, subsequent are users
    user_count = db.query(User).count()
    role = "admin" if user_count == 0 else "user"

    new_user = User(
        full_name=req.full_name.strip(),
        username=req.username.strip(),
        email=req.email.lower().strip(),
        password_hash=hash_password(req.password),
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # Create default settings
    default_settings = UserSettings(user_id=new_user.id)
    db.add(default_settings)
    db.commit()
    db.refresh(new_user)

    # Issue JWT token
    token = create_access_token({"sub": new_user.id, "email": new_user.email, "role": new_user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "created_at": new_user.created_at.isoformat()
        }
    }


@router.post("/login", response_model=TokenResponse)
def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticates user credentials and issues a JWT bearer token."""
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password combination."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat()
        }
    }


@router.post("/logout")
def logout_user():
    """Terminates client authenticated session."""
    return {"message": "Successfully logged out from TruthGuard Proof Desk."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns the authenticated user profile with real database summary statistics."""
    # Compute real user stats
    total_verifs = db.query(VerificationJob).filter(VerificationJob.user_id == current_user.id).count()
    avg_rel = db.query(func.avg(VerificationJob.reliability_score)).filter(VerificationJob.user_id == current_user.id).scalar() or 0.0
    total_inaccurate = (
        db.query(Claim)
        .join(VerificationJob, Claim.verification_id == VerificationJob.id)
        .filter(VerificationJob.user_id == current_user.id, Claim.predicted_label == "CONTRADICTED")
        .count()
    )

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "email": current_user.email,
        "profile_image": current_user.profile_image,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "total_verifications": total_verifs,
        "average_reliability": round(float(avg_rel) * 100, 1),
        "total_inaccurate_claims": total_inaccurate
    }


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Simulates sending a password reset token for account recovery."""
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user:
        # Avoid leaking whether an email exists
        return {"message": "If this email is registered, password reset instructions have been sent."}

    # Generate temporary reset token
    reset_token = create_access_token({"sub": user.id, "purpose": "reset_password"})
    return {
        "message": "If this email is registered, password reset instructions have been sent.",
        "reset_token": reset_token  # Provided for seamless local testing
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Resets user password with valid reset token."""
    from backend.app.auth.security import decode_access_token
    payload = decode_access_token(req.token)
    if not payload or payload.get("purpose") != "reset_password":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "Password successfully updated. You may now log in."}
