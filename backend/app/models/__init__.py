"""
TruthGuard SQLAlchemy Relational Models
Implements all entities: User, UserSettings, VerificationJob, Claim, Evidence, Correction, SavedResult, Feedback, AuditLog.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    auth_user_id = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(120), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    profile_image = Column(String(255), nullable=True)
    role = Column(String(20), default="user")  # 'user', 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    verifications = relationship("VerificationJob", back_populates="user", cascade="all, delete-orphan")
    saved_results = relationship("SavedResult", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(20), default="light")  # 'light', 'dark', 'system'
    language = Column(String(10), default="en")
    default_verification_mode = Column(String(50), default="standard")  # 'quick', 'standard', 'deep'
    default_correction_mode = Column(String(50), default="grounded")   # 'none', 'minimal', 'grounded'
    notification_preferences = Column(JSON, default=lambda: {
        "email_alerts": True,
        "verification_complete": True,
        "security_alerts": True
    })
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="settings")


class VerificationJob(Base):
    __tablename__ = "verification_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, default="Untitled Verification")
    original_text = Column(Text, nullable=False)
    optional_context = Column(Text, nullable=True)
    topic = Column(String(100), default="General")
    verification_mode = Column(String(50), default="standard")
    
    # Execution status: 'PENDING', 'EXTRACTING_CLAIMS', 'RETRIEVING_EVIDENCE', 'VERIFYING', 'SCORING', 'CORRECTING', 'COMPLETED', 'FAILED'
    processing_status = Column(String(30), default="COMPLETED")
    
    # M4 Reliability Metrics
    reliability_score = Column(Float, default=1.0)
    mean_rho = Column(Float, default=1.0)
    max_p_c = Column(Float, default=0.0)
    
    # Counts & Investigation Metrics
    total_claims = Column(Integer, default=0)
    supported_count = Column(Integer, default=0)
    contradicted_count = Column(Integer, default=0)
    nei_count = Column(Integer, default=0)
    support_rate = Column(Float, default=0.0)
    contradiction_rate = Column(Float, default=0.0)
    verification_coverage = Column(Float, default=0.0)
    unverified_rate = Column(Float, default=0.0)
    evidence_quality = Column(Float, default=0.85)
    
    # M5 Grounded Correction output
    corrected_text = Column(Text, nullable=True)
    corrections_count = Column(Integer, default=0)
    
    latency_sec = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="verifications")
    claims = relationship("Claim", back_populates="verification", cascade="all, delete-orphan", order_by="Claim.claim_number")
    corrections = relationship("Correction", back_populates="verification", cascade="all, delete-orphan")
    saved_items = relationship("SavedResult", back_populates="verification", cascade="all, delete-orphan")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    verification_id = Column(String(36), ForeignKey("verification_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_number = Column(Integer, nullable=False)
    claim_text = Column(Text, nullable=False)
    source_sentence = Column(Text, nullable=True)
    character_start = Column(Integer, default=0)
    character_end = Column(Integer, default=0)
    claim_type = Column(String(50), default="Relational")
    is_opinion = Column(Boolean, default=False)
    
    # Label: 'SUPPORTED', 'CONTRADICTED', 'NEI'
    predicted_label = Column(String(20), nullable=False)
    initial_label = Column(String(20), nullable=True)
    verdict_changed = Column(Boolean, default=False)
    change_reason = Column(Text, nullable=True)
    investigation_status = Column(String(30), default="COMPLETED")
    source_independence = Column(Float, default=1.0)
    p_supported = Column(Float, default=0.0)
    p_contradicted = Column(Float, default=0.0)
    p_nei = Column(Float, default=0.0)
    reliability = Column(Float, default=0.0)
    rationale = Column(Text, nullable=True)
    best_evidence = Column(Text, nullable=True)

    verification = relationship("VerificationJob", back_populates="claims")
    evidence_items = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan")
    corrections = relationship("Correction", back_populates="claim", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_text = Column(Text, nullable=False)
    source_title = Column(String(200), default="Knowledge Base")
    source_url = Column(String(500), nullable=True)
    retrieval_method = Column(String(50), default="Hybrid RRF")
    retrieval_score = Column(Float, default=0.0)
    authority_tier = Column(Integer, default=4)
    source_quality = Column(Float, default=0.50)
    publication_date = Column(String(50), nullable=True)
    rank = Column(Integer, default=1)

    claim = relationship("Claim", back_populates="evidence_items")


class Correction(Base):
    __tablename__ = "corrections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    verification_id = Column(String(36), ForeignKey("verification_jobs.id", ondelete="CASCADE"), nullable=False)
    original_claim = Column(Text, nullable=False)
    suggested_correction = Column(Text, nullable=False)
    evidence_used = Column(Text, nullable=True)
    verification_result = Column(String(20), default="SUPPORTED")
    accepted = Column(Boolean, default=True)
    correction_round = Column(Integer, default=1)
    rejection_reason = Column(Text, nullable=True)

    claim = relationship("Claim", back_populates="corrections")
    verification = relationship("VerificationJob", back_populates="corrections")


class SavedResult(Base):
    __tablename__ = "saved_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_id = Column(String(36), ForeignKey("verification_jobs.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_results")
    verification = relationship("VerificationJob", back_populates="saved_items")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(50), default="General")  # 'Bug', 'Feature', 'Accuracy', 'General'
    message = Column(Text, nullable=False)
    email = Column(String(120), nullable=True)
    status = Column(String(20), default="New")        # 'New', 'Reviewed', 'Resolved'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_logs")


class CitationAudit(Base):
    __tablename__ = "citation_audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    text = Column(Text, nullable=False)
    total_citations = Column(Integer, default=0)
    verified_count = Column(Integer, default=0)
    fabricated_count = Column(Integer, default=0)
    mismatch_count = Column(Integer, default=0)
    citations_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
