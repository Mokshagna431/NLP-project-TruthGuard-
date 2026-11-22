"""
TruthGuard Pydantic Schemas
Defines request and response schemas for all endpoints with strict data validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# --- Auth Schemas ---
class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    terms_accepted: bool = Field(..., description="Must accept terms of service")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: str
    full_name: str
    username: str
    email: str
    profile_image: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    total_verifications: Optional[int] = 0
    average_reliability: Optional[float] = 0.0
    total_inaccurate_claims: Optional[int] = 0

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    profile_image: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


# --- Settings Schemas ---
class UserSettingsResponse(BaseModel):
    theme: str
    language: str
    default_verification_mode: str
    default_correction_mode: str
    notification_preferences: Dict[str, Any]

    class Config:
        from_attributes = True


class UserSettingsUpdateRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    default_verification_mode: Optional[str] = None
    default_correction_mode: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None


# --- Verification & Claim Schemas ---
class VerificationCreateRequest(BaseModel):
    title: Optional[str] = "Untitled Verification"
    text: str = Field(..., min_length=5)
    context: Optional[str] = None
    topic: Optional[str] = "General"
    verification_mode: Optional[str] = "standard"  # 'quick', 'standard', 'deep'
    evidence_source: Optional[str] = "hybrid"      # 'context_only', 'knowledge_base', 'hybrid'
    decomposition_method: Optional[str] = "atomic_llm"
    verifier_type: Optional[str] = "nli"
    enable_correction: Optional[bool] = True
    tau_e: Optional[float] = 0.70
    tau_c: Optional[float] = 0.70
    lambda_nei: Optional[float] = 0.50


class EvidenceResponse(BaseModel):
    id: str
    evidence_text: str
    source_title: str
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    retrieval_method: str
    retrieval_score: float
    authority_tier: Optional[int] = 4
    source_quality: Optional[float] = 0.50
    rank: int

    class Config:
        from_attributes = True


class CorrectionResponse(BaseModel):
    id: str
    claim_id: str
    original_claim: str
    suggested_correction: str
    evidence_used: Optional[str] = None
    verification_result: str
    accepted: bool
    correction_round: int
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True


class ClaimResponse(BaseModel):
    id: str
    claim_number: int
    claim_text: str
    source_sentence: Optional[str] = None
    character_start: int
    character_end: int
    predicted_label: str  # 'SUPPORTED', 'CONTRADICTED', 'NEI'
    initial_label: Optional[str] = None
    verdict_changed: Optional[bool] = False
    change_reason: Optional[str] = None
    investigation_status: Optional[str] = "COMPLETED"
    source_independence: Optional[float] = 1.0
    p_supported: float
    p_contradicted: float
    p_nei: float
    reliability: float
    rationale: Optional[str] = None
    best_evidence: Optional[str] = None
    evidence_items: Optional[List[EvidenceResponse]] = []
    corrections: Optional[List[CorrectionResponse]] = []

    class Config:
        from_attributes = True


class VerificationJobResponse(BaseModel):
    id: str
    title: str
    original_text: str
    optional_context: Optional[str] = None
    topic: str
    verification_mode: str
    processing_status: str
    reliability_score: float
    mean_rho: float
    max_p_c: float
    total_claims: int
    supported_count: int
    contradicted_count: int
    nei_count: int
    support_rate: Optional[float] = 0.0
    contradiction_rate: Optional[float] = 0.0
    verification_coverage: Optional[float] = 0.0
    unverified_rate: Optional[float] = 0.0
    evidence_quality: Optional[float] = 0.85
    corrected_text: Optional[str] = None
    corrections_count: int
    latency_sec: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    claims: Optional[List[ClaimResponse]] = []
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True


class VerificationListResponse(BaseModel):
    items: List[VerificationJobResponse]
    total: int
    page: int
    page_size: int


# --- Analytics Schemas ---
class AnalyticsOverviewResponse(BaseModel):
    total_analyses: int
    total_claims_checked: int
    supported_claims: int
    contradicted_claims: int
    nei_claims: int
    average_reliability: float
    corrections_accepted: int
    corrections_rejected: int
    disputed_verdicts_percent: float


class AnalyticsTrendsResponse(BaseModel):
    daily_proofs: List[Dict[str, Any]]
    reliability_trend: List[Dict[str, Any]]
    busiest_hour: str
    calibration_commentary: str


class AnalyticsDistributionResponse(BaseModel):
    verdict_mix: Dict[str, int]
    topics_volume: List[Dict[str, Any]]


# --- Feedback & Admin Schemas ---
class FeedbackCreateRequest(BaseModel):
    category: str = "General"
    message: str = Field(..., min_length=5)
    email: Optional[EmailStr] = None


class FeedbackResponse(BaseModel):
    id: str
    category: str
    message: str
    email: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminOverviewResponse(BaseModel):
    total_users: int
    active_users: int
    total_verifications: int
    total_claims_processed: int
    system_status: str
    cpu_percent: float
    memory_percent: float
    loaded_models: List[str]
    recent_audit_logs: List[Dict[str, Any]]
