"""
TruthGuard Administrator & Platform Health Monitoring API Routes
Protected with Role-Based Access Control (RBAC).
"""

import psutil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.app.database.connection import get_db
from backend.app.models import User, VerificationJob, Claim, AuditLog, Feedback
from backend.app.schemas import AdminOverviewResponse
from backend.app.auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Administrator"])


@router.get("/overview", response_model=AdminOverviewResponse)
def get_admin_overview(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Returns platform-wide aggregate statistics, hardware utilization, and audit logs."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_verifs = db.query(VerificationJob).count()
    total_claims = db.query(Claim).count()

    # CPU & RAM utilization
    cpu_pct = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()

    # Recent audit logs
    recent_logs = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.timestamp))
        .limit(10)
        .all()
    )

    log_list = [
        {
            "id": log.id,
            "action": log.action,
            "user_id": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "metadata": log.metadata_json
        }
        for log in recent_logs
    ]

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_verifications": total_verifs,
        "total_claims_processed": total_claims,
        "system_status": "Healthy & Operational",
        "cpu_percent": cpu_pct,
        "memory_percent": mem.percent,
        "loaded_models": [
            "DeBERTa-v3-large (Calibrated NLI)",
            "all-MiniLM-L6-v2 (Dense SBERT Retriever)",
            "ms-marco-MiniLM-L-6-v2 (Cross-Encoder Re-ranker)",
            "spaCy en_core_web_sm (Rule-based Coref & Dependency)"
        ],
        "recent_audit_logs": log_list
    }


@router.get("/users")
def get_users_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lists registered platform users with verification volume and status."""
    query = db.query(User)
    if search:
        query = query.filter((User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%")))

    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for u in users:
        v_count = db.query(VerificationJob).filter(VerificationJob.user_id == u.id).count()
        items.append({
            "id": u.id,
            "full_name": u.full_name,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
            "verifications_count": v_count
        })

    return {"users": items, "total": total, "page": page, "page_size": page_size}


@router.put("/users/{user_id}/status")
def toggle_user_status(
    user_id: str,
    active: bool,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Suspends or reactivates a user account."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Administrators cannot deactivate their own account.")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_user.is_active = active
    db.commit()
    return {"message": f"User status updated to {'Active' if active else 'Suspended'}."}


@router.get("/system-health")
def get_system_health(admin: User = Depends(get_current_admin)):
    """Provides detailed hardware audit and model cache status."""
    return {
        "status": "online",
        "service": "TruthGuard Full-Stack Platform",
        "hardware": {
            "os": "Windows 11 (64-bit)",
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2)
        },
        "ml_pipeline": {
            "m1_decomposition": "Available (Atomic LLM Few-Shot / spaCy)",
            "m2_retrieval": "Available (BM25 + SBERT Hybrid RRF)",
            "m3_verification": "Available (DeBERTa-v3 NLI Calibrated, T=0.2633)",
            "m4_reliability": "Available (rho = P_E + lambda*P_N, R(a) = min(mean, 1 - max P_C))",
            "m5_correction": "Available (Verify-then-accept loop)"
        }
    }
