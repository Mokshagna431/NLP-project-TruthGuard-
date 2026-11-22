-- =============================================================================
-- TRUTHGUARD PRODUCTION POSTGRESQL RELATIONAL SCHEMA
-- Evidence-Grounded, Claim-Level Hallucination Detection & Correction Platform
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    auth_user_id VARCHAR(100) UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 2. User Settings Table
CREATE TABLE IF NOT EXISTS user_settings (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'light' CHECK (theme IN ('light', 'dark', 'system')),
    language VARCHAR(10) DEFAULT 'en',
    default_verification_mode VARCHAR(50) DEFAULT 'standard',
    default_correction_mode VARCHAR(50) DEFAULT 'grounded',
    notification_preferences JSONB DEFAULT '{"email_alerts": true, "verification_complete": true, "security_alerts": true}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Verification Jobs Table
CREATE TABLE IF NOT EXISTS verification_jobs (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL DEFAULT 'Untitled Verification',
    original_text TEXT NOT NULL,
    optional_context TEXT,
    topic VARCHAR(100) DEFAULT 'General',
    verification_mode VARCHAR(50) DEFAULT 'standard',
    processing_status VARCHAR(30) DEFAULT 'COMPLETED' CHECK (
        processing_status IN ('PENDING', 'EXTRACTING_CLAIMS', 'RETRIEVING_EVIDENCE', 'VERIFYING', 'SCORING', 'CORRECTING', 'COMPLETED', 'FAILED')
    ),
    reliability_score DOUBLE PRECISION DEFAULT 1.0,
    mean_rho DOUBLE PRECISION DEFAULT 1.0,
    max_p_c DOUBLE PRECISION DEFAULT 0.0,
    total_claims INTEGER DEFAULT 0,
    supported_count INTEGER DEFAULT 0,
    contradicted_count INTEGER DEFAULT 0,
    nei_count INTEGER DEFAULT 0,
    corrected_text TEXT,
    corrections_count INTEGER DEFAULT 0,
    latency_sec DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON verification_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON verification_jobs(created_at);

-- 4. Claims Table
CREATE TABLE IF NOT EXISTS claims (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    verification_id VARCHAR(36) NOT NULL REFERENCES verification_jobs(id) ON DELETE CASCADE,
    claim_number INTEGER NOT NULL,
    claim_text TEXT NOT NULL,
    source_sentence TEXT,
    character_start INTEGER DEFAULT 0,
    character_end INTEGER DEFAULT 0,
    claim_type VARCHAR(50) DEFAULT 'Relational',
    is_opinion BOOLEAN DEFAULT FALSE,
    predicted_label VARCHAR(20) NOT NULL CHECK (predicted_label IN ('SUPPORTED', 'CONTRADICTED', 'NEI')),
    p_supported DOUBLE PRECISION DEFAULT 0.0,
    p_contradicted DOUBLE PRECISION DEFAULT 0.0,
    p_nei DOUBLE PRECISION DEFAULT 0.0,
    reliability DOUBLE PRECISION DEFAULT 0.0,
    rationale TEXT,
    best_evidence TEXT
);

CREATE INDEX IF NOT EXISTS idx_claims_verification_id ON claims(verification_id);
CREATE INDEX IF NOT EXISTS idx_claims_label ON claims(predicted_label);

-- 5. Evidence Table
CREATE TABLE IF NOT EXISTS evidence (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    claim_id VARCHAR(36) NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    evidence_text TEXT NOT NULL,
    source_title VARCHAR(200) DEFAULT 'Knowledge Base',
    source_url VARCHAR(500),
    retrieval_method VARCHAR(50) DEFAULT 'Hybrid RRF',
    retrieval_score DOUBLE PRECISION DEFAULT 0.0,
    authority_tier INTEGER DEFAULT 4,
    source_quality DOUBLE PRECISION DEFAULT 0.50,
    publication_date VARCHAR(50),
    rank INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_evidence_claim_id ON evidence(claim_id);

-- 6. Corrections Table
CREATE TABLE IF NOT EXISTS corrections (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    claim_id VARCHAR(36) NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    verification_id VARCHAR(36) NOT NULL REFERENCES verification_jobs(id) ON DELETE CASCADE,
    original_claim TEXT NOT NULL,
    suggested_correction TEXT NOT NULL,
    evidence_used TEXT,
    verification_result VARCHAR(20) DEFAULT 'SUPPORTED' CHECK (verification_result IN ('SUPPORTED', 'CONTRADICTED', 'NEI', 'REJECTED')),
    accepted BOOLEAN DEFAULT TRUE,
    correction_round INTEGER DEFAULT 1,
    rejection_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_corrections_verification_id ON corrections(verification_id);

-- 7. Saved Results Table
CREATE TABLE IF NOT EXISTS saved_results (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verification_id VARCHAR(36) NOT NULL REFERENCES verification_jobs(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, verification_id)
);

CREATE INDEX IF NOT EXISTS idx_saved_user_id ON saved_results(user_id);

-- 8. Feedback Table
CREATE TABLE IF NOT EXISTS feedback (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    category VARCHAR(50) DEFAULT 'General',
    message TEXT NOT NULL,
    email VARCHAR(120),
    status VARCHAR(20) DEFAULT 'New' CHECK (status IN ('New', 'Reviewed', 'Resolved')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata_json JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id);

-- 10. Citation Audits Table
CREATE TABLE IF NOT EXISTS citation_audits (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    text TEXT NOT NULL,
    total_citations INTEGER DEFAULT 0,
    verified_count INTEGER DEFAULT 0,
    fabricated_count INTEGER DEFAULT 0,
    mismatch_count INTEGER DEFAULT 0,
    citations_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_citation_audits_user ON citation_audits(user_id);
