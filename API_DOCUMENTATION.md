# TruthGuard 3.0: REST API Documentation

**Base URL**: `http://localhost:8000/api`  
**Authentication**: Bearer JWT token in HTTP header `Authorization: Bearer <token>`

---

## 1. Authentication Endpoints (`/api/auth`)

### `POST /api/auth/register`
Creates a new user account.
- **Request Body**:
  ```json
  {
    "full_name": "Dr. Mokshagna",
    "username": "mokshagna",
    "email": "user@truthguard.ai",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "user": { "id": "uuid", "username": "mokshagna", "role": "admin" }
  }
  ```

### `POST /api/auth/login`
Authenticates existing user.
- **Request Body**: `{"username": "mokshagna", "password": "SecurePassword123!"}`
- **Response (200 OK)**: Token and user object.

### `GET /api/auth/me`
Retrieves currently authenticated user profile and verification statistics.

---

## 2. Verification Endpoints (`/api/verification`)

### `POST /api/verification`
Executes complete M1–M5 pipeline on submitted text.
- **Request Body**:
  ```json
  {
    "title": "Renaissance Historical Audit",
    "text": "The Renaissance spanned from the 17th to 20th centuries, centered in Asia.",
    "context": "The Renaissance occurred from the 14th to 17th centuries in Europe.",
    "verification_mode": "standard",
    "decomposition_method": "atomic_llm",
    "evidence_source": "hybrid",
    "verifier_type": "nli",
    "enable_correction": true
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "id": "e932da12-...",
    "title": "Renaissance Historical Audit",
    "reliability_score": 0.048,
    "mean_rho": 0.048,
    "max_p_c": 0.962,
    "supported_count": 0,
    "contradicted_count": 1,
    "nei_count": 0,
    "corrected_text": "The Renaissance occurred from the 14th to 17th centuries, primarily in Europe.",
    "latency_sec": 0.42,
    "claims": [
      {
        "id": "claim-1",
        "claim_number": 1,
        "claim_text": "The Renaissance spanned from the 17th to 20th centuries, centered in Asia.",
        "predicted_label": "CONTRADICTED",
        "p_supported": 0.012,
        "p_contradicted": 0.962,
        "p_nei": 0.026,
        "reliability": 0.025,
        "best_evidence": "The Renaissance actually occurred from the 14th to the 17th centuries, primarily in Europe, not Asia.",
        "evidence_items": [
          {
            "source_title": "Encyclopedic Reference",
            "source_url": "https://en.wikipedia.org/wiki/Renaissance",
            "retrieval_method": "hybrid",
            "retrieval_score": 0.94
          }
        ],
        "corrections": [
          {
            "suggested_correction": "The Renaissance spanned from the 14th to 17th centuries, centered in Europe.",
            "accepted": true
          }
        ]
      }
    ]
  }
  ```

### `GET /api/verification`
Lists user's previous audits with pagination, search, and date filters.

### `GET /api/verification/{id}`
Retrieves complete claim-level audit details for a specific verification.

### `POST /api/verification/{id}/rerun`
Re-runs an existing audit using the latest pipeline models.

---

## 3. Academic Citation Verification (`/api/citation`)

### `POST /api/citation/verify`
Extracts and verifies DOIs, ArXiv IDs, and bibliographic entries against Crossref and Semantic Scholar.
- **Request Body**:
  ```json
  {
    "text": "Self-attention was introduced in 10.5555/3295222.3295349 by Vaswani et al. (2017)."
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "total_citations": 1,
    "counts": {
      "VERIFIED": 1,
      "PARTIALLY_VERIFIED": 0,
      "CITATION_MISMATCH": 0,
      "POTENTIALLY_FABRICATED": 0,
      "UNAVAILABLE": 0
    },
    "citations": [
      {
        "citation": { "raw_text": "10.5555/3295222.3295349", "type": "doi" },
        "status": "VERIFIED",
        "confidence": 0.98,
        "rationale": "Verified against academic record: 'Attention Is All You Need' (2017).",
        "registry_data": {
          "title": "Attention Is All You Need",
          "authors": ["Ashish Vaswani", "Noam Shazeer"],
          "year": 2017,
          "venue": "NeurIPS"
        }
      }
    ]
  }
  ```

---

## 4. Reports & Exports (`/api/reports`)

- `GET /api/reports/{id}/pdf`: Downloads official publication ReportLab PDF.
- `GET /api/reports/{id}/csv`: Exports claim audit matrix in CSV format.
- `GET /api/reports/{id}/json`: Downloads raw verification JSON payload.
- `GET /api/reports/{id}/txt`: Downloads corrected answer plain text.

---

## 5. System Health & Hardware Audit (`/api/health`)

- `GET /api/health`: Returns active database status, PyTorch accelerator, and loaded model names.
