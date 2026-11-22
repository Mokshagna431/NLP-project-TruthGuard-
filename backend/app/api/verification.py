"""
TruthGuard Verification & Claim Audit API Routes
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime, timedelta

from backend.app.database.connection import get_db
from backend.app.models import User, VerificationJob, Claim, Evidence, Correction, SavedResult
from backend.app.schemas import (
    VerificationCreateRequest, VerificationJobResponse,
    VerificationListResponse, ClaimResponse, CorrectionResponse
)
from backend.app.auth.dependencies import get_current_user, get_optional_user
from backend.app.services.verification_service import VerificationService

router = APIRouter(prefix="/api/verification", tags=["Verification"])
saved_router = APIRouter(prefix="/api/saved", tags=["Saved Results"])


@router.post("", response_model=VerificationJobResponse)
def create_verification(
    req: VerificationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submits LLM text for M1-M5 hallucination detection, scoring, and grounded correction."""
    try:
        job = VerificationService.run_and_save(
            db=db,
            user_id=current_user.id,
            title=req.title or "Untitled Verification",
            text=req.text,
            context=req.context,
            topic=req.topic or "General",
            verification_mode=req.verification_mode or "standard",
            decomposition_method=req.decomposition_method or "atomic_llm",
            retrieval_mode=req.evidence_source or "hybrid",
            verifier_type=req.verifier_type or "nli",
            enable_correction=req.enable_correction,
            tau_e=req.tau_e or 0.70,
            tau_c=req.tau_c or 0.70,
            lambda_nei=req.lambda_nei or 0.50
        )
        return job
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification pipeline error: {str(e)}"
        )


@router.get("", response_model=VerificationListResponse)
def list_verifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    days: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists current user's past verifications with full search, date filter, status, and sorting."""
    query = db.query(VerificationJob).filter(VerificationJob.user_id == current_user.id)

    if search:
        query = query.filter(
            (VerificationJob.title.ilike(f"%{search}%")) |
            (VerificationJob.original_text.ilike(f"%{search}%"))
        )

    if status_filter and status_filter != "all":
        query = query.filter(VerificationJob.processing_status == status_filter.upper())

    if days:
        since_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(VerificationJob.created_at >= since_date)

    total = query.count()

    # Sorting
    sort_col = getattr(VerificationJob, sort_by, VerificationJob.created_at)
    if sort_order == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    # Check if saved
    saved_ids = set(
        db.query(SavedResult.verification_id)
        .filter(SavedResult.user_id == current_user.id)
        .all()
    )

    for item in items:
        item.is_saved = (item.id,) in saved_ids

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{verification_id}", response_model=VerificationJobResponse)
def get_verification_details(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns complete claim-level audit for a specific verification job."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    is_saved = db.query(SavedResult).filter(
        SavedResult.user_id == current_user.id,
        SavedResult.verification_id == job.id
    ).first() is not None

    job.is_saved = is_saved
    return job


@router.post("/{verification_id}/rerun", response_model=VerificationJobResponse)
def rerun_verification(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Re-executes hallucination verification on an existing record."""
    old_job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not old_job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    new_job = VerificationService.run_and_save(
        db=db,
        user_id=current_user.id,
        title=f"{old_job.title} (Re-run)",
        text=old_job.original_text,
        context=old_job.optional_context,
        topic=old_job.topic,
        verification_mode=old_job.verification_mode
    )
    return new_job


@router.delete("/{verification_id}")
def delete_verification(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a verification job and all its associated claim records."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    db.delete(job)
    db.commit()
    return {"message": "Verification record successfully deleted."}


@router.get("/{verification_id}/claims", response_model=List[ClaimResponse])
def get_verification_claims(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns atomic claims breakdown for a verification analysis."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    return job.claims


@router.get("/{verification_id}/corrections", response_model=List[CorrectionResponse])
def get_verification_corrections(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns M5 Grounded Correction audit trail for a verification analysis."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    return job.corrections


# --- Saved Results Routes ---
@router.post("/{verification_id}/save")
def save_verification_result(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bookmarks/saves a verification result for quick retrieval."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    existing = db.query(SavedResult).filter(
        SavedResult.user_id == current_user.id,
        SavedResult.verification_id == verification_id
    ).first()

    if existing:
        return {"message": "Verification is already in saved cases.", "saved": True}

    saved = SavedResult(user_id=current_user.id, verification_id=verification_id)
    db.add(saved)
    db.commit()
    return {"message": "Case saved to bookmarks.", "saved": True}


@saved_router.delete("/{verification_id}")
def remove_saved_verification(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Removes a verification result from saved bookmarks."""
    item = db.query(SavedResult).filter(
        SavedResult.user_id == current_user.id,
        SavedResult.verification_id == verification_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Saved case not found.")

    db.delete(item)
    db.commit()
    return {"message": "Case removed from saved items.", "saved": False}


@saved_router.get("", response_model=List[VerificationJobResponse])
def get_saved_verifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns all bookmarked verification jobs for the authenticated user."""
    items = (
        db.query(VerificationJob)
        .join(SavedResult, VerificationJob.id == SavedResult.verification_id)
        .filter(SavedResult.user_id == current_user.id)
        .order_by(desc(SavedResult.created_at))
        .all()
    )
    for job in items:
        job.is_saved = True
    return items
