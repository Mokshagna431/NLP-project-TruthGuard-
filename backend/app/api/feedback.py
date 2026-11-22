"""
TruthGuard Feedback & Inquiry API Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.connection import get_db
from backend.app.models import Feedback, User
from backend.app.schemas import FeedbackCreateRequest, FeedbackResponse
from backend.app.auth.dependencies import get_optional_user

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    req: FeedbackCreateRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Submits user feedback, bug report, or model accuracy commentary."""
    fb = Feedback(
        user_id=current_user.id if current_user else None,
        category=req.category,
        message=req.message.strip(),
        email=req.email or (current_user.email if current_user else None),
        status="New"
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@router.get("", response_model=List[FeedbackResponse])
def get_user_feedback(
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Lists feedback submitted by the user."""
    if not current_user:
        return []
    return (
        db.query(Feedback)
        .filter(Feedback.user_id == current_user.id)
        .order_by(desc(Feedback.created_at))
        .all()
    )
