# TruthGuard: Complete Full-Stack AI Hallucination Detection & Proof Desk Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/Frontend-React%20%2B%20Vite%20%2B%20Tailwind-purple.svg)](https://vitejs.dev/)
[![SQLAlchemy](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-red.svg)](https://www.sqlalchemy.org/)
[![Status](https://img.shields.io/badge/Status-Complete%20%26%20Verified-success.svg)]()

> A full-stack AI SaaS platform for **evidence-grounded, claim-level hallucination detection, scoring, and grounded correction** in Large Language Model outputs. Built with real ML pipelines, database persistence, JWT authentication, user-specific analytics, ReportLab PDF report generation, and role-based access control.

---

## 1. System Architecture

```
                          TRUTHGUARD ARCHITECTURE
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React + Vite)                           │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │ Public Landing, About│  │ Editorial Proof Desk │  │ Dual-Panel Audit & │ │
│  │ & Docs Pages         │  │ Analytics Dashboard  │  │ Side-by-Side Diffs │ │
│  └──────────┬───────────┘  └──────────┬───────────┘  └────────┬───────────┘ │
│             │                         │                       │             │
│             └─────────────────────────┼───────────────────────┘             │
│                                       ▼                                     │
│                        Axios/Fetch Client with Bearer JWT                   │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │ HTTP REST
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI + SQLAlchemy)                        │
│  ┌───────────────────┐  ┌───────────────────────┐  ┌──────────────────────┐ │
│  │ Auth & Security   │  │ Verification Engine   │  │ PDF / CSV Exports    │ │
│  │ (Bcrypt, JWT)     │  │ & Async Pipeline      │  │ (ReportLab Service)  │ │
│  └─────────┬─────────┘  └───────────┬───────────┘  └──────────┬───────────┘ │
│            │                        │                         │             │
│            ▼                        ▼                         ▼             │
│  ┌───────────────────┐  ┌───────────────────────┐  ┌──────────────────────┐ │
│  │ PostgreSQL /      │  │ TruthGuard Pipeline   │  │ Analytics &          │ │
│  │ SQLite Fallback   │  │ (M1, M2, M3, M4, M5)  │  │ RBAC Administration  │ │
│  └───────────────────┘  └───────────────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Relational Database Schema (`database/schema.sql`)

The database implements 9 relational tables:
1. **`users`**: Authentication credentials, hashed passwords (`bcrypt`), roles (`user`/`admin`), and active flags.
2. **`user_settings`**: Personal themes (`light`/`dark`), languages, default verification modes, and notification preferences.
3. **`verification_jobs`**: Job records, processing stages (`COMPLETED`, `FAILED`), M4 reliability score $R(a)$, mean $\bar{\rho}$, max $P_C$, claim counts, corrected answer, and latencies.
4. **`claims`**: Atomic claim extractions, source sentences, character offsets, predicted labels (`SUPPORTED`, `CONTRADICTED`, `NEI`), calibrated probabilities ($P_E, P_C, P_N$), and reliability $\rho(c)$.
5. **`evidence`**: Candidate retrieved evidence passages, source titles, URLs, retrieval methods (`Hybrid RRF`, `SBERT`, `BM25`), and cross-encoder relevance scores.
6. **`corrections`**: M5 verify-then-accept records, original claims, proposed corrections, and acceptance flags.
7. **`saved_results`**: User bookmarks and case tags.
8. **`feedback`**: Inquiries, bug reports, and model accuracy submissions.
9. **`audit_logs`**: Platform activity timestamps and metadata.

---

## 3. The 5 Core Verification Modules (M1–M5)

- **[M1] Claim Decomposition**: Coreference resolution (spaCy) and atomic proposition splitting with character offset tracking.
- **[M2] Evidence Retrieval**: Sparse BM25 + dense Sentence-BERT combined via Reciprocal Rank Fusion (RRF) with MiniLM Cross-Encoder re-ranking and retrieval gate threshold $\tau_r$.
- **[M3] Claim Verification**: Calibrated DeBERTa-v3 NLI with sentence-max aggregation and conservative tie-breaking to avoid false penalties.
- **[M4] Non-Compensatory Reliability**:
  $$\rho(c) = P_E(c) + \lambda \times P_N(c)$$
  $$R(a) = \min\left(\frac{1}{|C|}\sum \rho(c),\, 1 - \max_c P_C(c)\right)$$
- **[M5] Grounded Correction**: Verify-then-accept revision loop rewriting contradicted claims against retrieved evidence.

---

## 4. Quick Start & Execution

### 4.1 Launch Backend (FastAPI, Port 8000)
```powershell
.\run_backend.bat
# Or manually:
python -m backend.server
```
- Swagger Interactive Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 4.2 Launch Frontend (React + Vite, Port 5173)
```powershell
.\run_frontend.bat
# Or manually:
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 5. Running Automated Test Suites

```powershell
# Run the complete full-stack platform backend test suite:
python tests/test_full_platform_backend.py

# Run Phase 1-3 M1-M3 unit tests:
python -m tests.test_decompose
python -m tests.test_retrieve
python -m tests.test_verify

# Run full end-to-end pipeline test:
python -m tests.test_pipeline_e2e
```

---

## 6. Report Downloads & Exports

Every verification job can be exported in 4 formats:
- **PDF Report**: `GET /api/reports/{id}/pdf` — Official ReportLab audit certificate with reliability gauge, claim breakdown table, and grounded corrections.
- **CSV Data**: `GET /api/reports/{id}/csv` — Claim-level spreadsheet with probabilities and verdicts.
- **JSON Artifact**: `GET /api/reports/{id}/json` — Complete structured provenance artifact.
- **TXT Answer**: `GET /api/reports/{id}/txt` — Clean verified revised text.

---

## 7. Administrator Console & RBAC

The first registered user is automatically granted the `admin` role.
- **User Governance**: Inspect platform users, check verification counts, and suspend/reactivate accounts.
- **System Telemetry**: Real-time CPU, RAM, and loaded ML model caches (`DeBERTa-v3`, `all-MiniLM-L6-v2`, `CrossEncoder`, `spaCy`).
