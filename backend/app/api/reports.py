"""
TruthGuard Reports & Export API Routes (PDF, CSV, JSON, TXT)
"""

import io
import csv
import json
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models import User, VerificationJob
from backend.app.auth.dependencies import get_current_user
from backend.app.services.pdf_service import PDFReportService

router = APIRouter(prefix="/api/reports", tags=["Reports & Exports"])


@router.get("/{verification_id}/pdf")
def export_verification_pdf(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates and streams an official TruthGuard PDF audit certificate."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    pdf_buffer = PDFReportService.generate_verification_report(job)
    filename = f"TruthGuard_Report_{job.id[:8]}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{verification_id}/csv")
def export_verification_csv(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports claim-level verification records as a CSV spreadsheet."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Claim_Number", "Claim_Text", "Verdict", "P_Supported",
        "P_Contradicted", "P_NEI", "Reliability_Rho", "Best_Evidence", "Source_Sentence"
    ])

    for claim in job.claims:
        writer.writerow([
            claim.claim_number,
            claim.claim_text,
            claim.predicted_label,
            f"{claim.p_supported:.4f}",
            f"{claim.p_contradicted:.4f}",
            f"{claim.p_nei:.4f}",
            f"{claim.reliability:.4f}",
            claim.best_evidence or "",
            claim.source_sentence or ""
        ])

    output.seek(0)
    filename = f"TruthGuard_Claims_{job.id[:8]}.csv"

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{verification_id}/json")
def export_verification_json(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports complete structured verification JSON artifact."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    data = {
        "id": job.id,
        "title": job.title,
        "created_at": job.created_at.isoformat(),
        "reliability_score": job.reliability_score,
        "mean_rho": job.mean_rho,
        "max_p_c": job.max_p_c,
        "total_claims": job.total_claims,
        "counts": {
            "n_S": job.supported_count,
            "n_C": job.contradicted_count,
            "n_NEI": job.nei_count
        },
        "original_text": job.original_text,
        "corrected_text": job.corrected_text,
        "claims": [
            {
                "claim_number": c.claim_number,
                "claim": c.claim_text,
                "label": c.predicted_label,
                "p_e": c.p_supported,
                "p_c": c.p_contradicted,
                "p_n": c.p_nei,
                "rho": c.reliability,
                "evidence": c.best_evidence,
                "evidence_list": [e.evidence_text for e in c.evidence_items]
            }
            for c in job.claims
        ],
        "corrections": [
            {
                "original_claim": corr.original_claim,
                "suggested_correction": corr.suggested_correction,
                "accepted": corr.accepted,
                "evidence_used": corr.evidence_used
            }
            for corr in job.corrections
        ]
    }

    filename = f"TruthGuard_Data_{job.id[:8]}.json"
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{verification_id}/txt")
def export_corrected_text(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Downloads the M5 ground-corrected text as a plain text file."""
    job = (
        db.query(VerificationJob)
        .filter(VerificationJob.id == verification_id, VerificationJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Verification analysis not found.")

    text_content = job.corrected_text or job.original_text
    filename = f"TruthGuard_Corrected_{job.id[:8]}.txt"

    return Response(
        content=text_content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
