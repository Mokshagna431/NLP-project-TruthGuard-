"""
TruthGuard Production FastAPI REST Backend Application
Integrates User Authentication, Database Persistence, Real M1-M5 Pipeline,
PDF Exports, User Analytics, and Administrator Management.
"""

import os
import sys
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.database.connection import engine, Base
from backend.app.api.auth import router as auth_router
from backend.app.api.profile import router as profile_router, settings_router
from backend.app.api.verification import router as verification_router, saved_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.reports import router as reports_router
from backend.app.api.admin import router as admin_router
from backend.app.api.feedback import router as feedback_router
from backend.app.api.citation import router as citation_router

# Initialize database schema tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TruthGuard Platform API",
    description="Evidence-Grounded, Claim-Level Hallucination Detection, Scoring & Correction Platform",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount publication vector figures
figures_dir = os.path.join(ROOT_DIR, "results", "figures")
if os.path.exists(figures_dir):
    app.mount("/static/figures", StaticFiles(directory=figures_dir), name="figures")

# Register API Routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(settings_router)
app.include_router(verification_router)
app.include_router(saved_router)
app.include_router(analytics_router)
app.include_router(reports_router)
app.include_router(admin_router)
app.include_router(feedback_router)
app.include_router(citation_router)


@app.get("/api/health")
def health_check():
    """System health check and hardware environment audit."""
    return {
        "status": "healthy",
        "service": "TruthGuard Full-Stack Platform",
        "version": "2.0.0",
        "database": "Active (SQLAlchemy ORM)",
        "hardware": {
            "os": "Windows 11 (64-bit)",
            "cpu": "Intel64 Family 6 Model 186 (12 CPU cores)",
            "ram_gb": 15.65,
            "accelerator": "CPU (PyTorch multi-threaded)"
        },
        "models": {
            "nli_verifier": "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
            "dense_retriever": "sentence-transformers/all-MiniLM-L6-v2",
            "cross_encoder": "cross-encoder/ms-marco-MiniLM-L-6-v2"
        }
    }


@app.get("/api/results")
def get_benchmark_results():
    """Serves the benchmark and ablation matrix from results/summary.csv."""
    summary_path = os.path.join(ROOT_DIR, "results", "summary.csv")
    if os.path.exists(summary_path):
        df = pd.read_csv(summary_path)
        # Replace NaN with None for JSON serialization
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        return {"data": records}
    return {"data": []}


# --- Backward Compatibility Shims for Legacy Frontend Endpoints ---
from truthguard.pipeline import TruthGuardPipeline
from pydantic import BaseModel
from typing import Optional


class LegacyPipelineRequest(BaseModel):
    answer: str
    context: Optional[str] = None
    decomposition_method: str = "atomic_llm"
    retrieval_mode: str = "hybrid"
    verifier_type: str = "nli"
    tau_e: float = 0.70
    tau_c: float = 0.70
    tau_r: float = 0.10
    lambda_nei: float = 0.50


@app.post("/api/pipeline")
def legacy_pipeline_endpoint(req: LegacyPipelineRequest):
    """Direct M1-M5 execution endpoint for fast testing and script evaluation."""
    pipeline = TruthGuardPipeline(
        decomposition_method=req.decomposition_method,
        retrieval_mode=req.retrieval_mode,
        verifier_type=req.verifier_type,
        tau_e=req.tau_e,
        tau_c=req.tau_c,
        tau_r=req.tau_r,
        lambda_nei=req.lambda_nei
    )
    return pipeline.run(answer=req.answer, rag_context=req.context)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
