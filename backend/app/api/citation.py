"""
TruthGuard Academic Citation Verification API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from truthguard.citation import CitationVerifier
from backend.app.models import User
from backend.app.auth.dependencies import get_optional_user

router = APIRouter(prefix="/api/citation", tags=["Citation Verification"])
_verifier = CitationVerifier()


class CitationVerifyRequest(BaseModel):
    text: str


@router.post("/verify")
def verify_text_citations(req: CitationVerifyRequest):
    """Parses and verifies all academic citations, DOIs, and literature references in text."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        results = _verifier.verify_all_in_text(req.text)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Citation verification error: {str(e)}")
