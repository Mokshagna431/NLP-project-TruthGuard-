"""
Comprehensive Backend Test Suite for TruthGuard Full-Stack Platform
Tests: Authentication, Database Persistence, Verification Pipeline,
PDF/CSV Generation, Analytics, and RBAC Admin Control.
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure root directory is on PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Force test SQLite DB
os.environ["DATABASE_URL"] = "sqlite:///./test_truthguard.db"

from backend.app.main import app
from backend.app.database.connection import engine, Base


class TestTruthGuardFullPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create fresh test tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Clean up test DB
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_truthguard.db"):
            try:
                os.remove("./test_truthguard.db")
            except Exception:
                pass

    def test_01_health_check(self):
        """Tests health check endpoint returns 200 OK and environment audit."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("TruthGuard", data["service"])

    def test_02_user_registration_and_login(self):
        """Tests user registration (first user becomes admin) and JWT login."""
        # Register Admin User
        reg_payload = {
            "full_name": "Dr. Miriam Okafor",
            "username": "mokafor",
            "email": "mokafor@meridian.org",
            "password": "SecurePassword123!",
            "terms_accepted": True
        }
        res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "admin")
        self.assertEqual(data["user"]["username"], "mokafor")

        # Login
        login_res = self.client.post("/api/auth/login", json={
            "email": "mokafor@meridian.org",
            "password": "SecurePassword123!"
        })
        self.assertEqual(login_res.status_code, 200)
        self.admin_token = login_res.json()["access_token"]

        # Verify /api/auth/me
        me_res = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["username"], "mokafor")

    def test_03_verification_pipeline_and_db_storage(self):
        """Tests full M1-M5 execution, database storage of claims, and scoring."""
        # Login first to get token
        login_res = self.client.post("/api/auth/login", json={
            "email": "mokafor@meridian.org",
            "password": "SecurePassword123!"
        })
        token = login_res.json()["access_token"]

        verify_payload = {
            "title": "Eiffel Tower Hallucination Audit",
            "text": "The Eiffel Tower was constructed in 1892 and was designed by Leonardo da Vinci.",
            "context": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair. The tower was designed by Maurice Koechlin and Emile Nouguier, and built by Gustave Eiffel's civil engineering company.",
            "decomposition_method": "rule_based",
            "verifier_type": "similarity",
            "evidence_source": "hybrid",
            "enable_correction": False
        }

        res = self.client.post(
            "/api/verification",
            json=verify_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        job = res.json()

        self.assertIn("id", job)
        self.assertEqual(job["processing_status"], "COMPLETED")
        self.assertGreaterEqual(len(job["claims"]), 1)
        self.assertGreaterEqual(job["total_claims"], 1)

        # Save verification ID for subsequent tests
        TestTruthGuardFullPlatform.job_id = job["id"]
        TestTruthGuardFullPlatform.user_token = token

    def test_04_verification_get_details(self):
        """Tests retrieval of verification details by ID."""
        job_id = TestTruthGuardFullPlatform.job_id
        token = TestTruthGuardFullPlatform.user_token

        res = self.client.get(
            f"/api/verification/{job_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        job = res.json()
        self.assertEqual(job["id"], job_id)
        self.assertTrue(len(job["claims"]) >= 2)

    def test_05_pdf_report_generation(self):
        """Tests ReportLab PDF report generation and binary response."""
        job_id = TestTruthGuardFullPlatform.job_id
        token = TestTruthGuardFullPlatform.user_token

        res = self.client.get(
            f"/api/reports/{job_id}/pdf",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers["content-type"], "application/pdf")
        # PDF magic bytes check
        self.assertTrue(res.content.startswith(b"%PDF-"))
        self.assertGreater(len(res.content), 1000)

    def test_06_csv_export(self):
        """Tests CSV export generation."""
        job_id = TestTruthGuardFullPlatform.job_id
        token = TestTruthGuardFullPlatform.user_token

        res = self.client.get(
            f"/api/reports/{job_id}/csv",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Claim_Number,Claim_Text,Verdict", res.text)

    def test_07_analytics_overview(self):
        """Tests user analytics calculating real statistics from DB."""
        token = TestTruthGuardFullPlatform.user_token
        res = self.client.get(
            "/api/analytics/overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_analyses"], 1)
        self.assertGreater(data["total_claims_checked"], 0)

    def test_08_feedback_submission(self):
        """Tests feedback submission endpoint."""
        token = TestTruthGuardFullPlatform.user_token
        res = self.client.post(
            "/api/feedback",
            json={
                "category": "Accuracy",
                "message": "The M5 Grounded Correction resolved the Leonardo da Vinci hallucination cleanly."
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "New")

    def test_09_admin_overview_and_rbac(self):
        """Tests admin overview and RBAC authorization."""
        token = TestTruthGuardFullPlatform.user_token
        res = self.client.get(
            "/api/admin/overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_users"], 1)
        self.assertGreaterEqual(data["total_verifications"], 1)
        self.assertEqual(data["system_status"], "Healthy & Operational")

    def test_10_math_hallucination_detection_and_correction(self):
        """Tests detection and grounded correction of mathematical hallucinations (e.g. 2+2=7 -> 2+2=4)."""
        token = TestTruthGuardFullPlatform.user_token
        res = self.client.post(
            "/api/verification",
            json={
                "title": "Mathematics Test Case",
                "text": "2+2=7",
                "verifier_type": "similarity"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["contradicted_count"], 1)
        self.assertEqual(data["corrected_text"], "2+2=4")
        self.assertEqual(data["claims"][0]["predicted_label"], "CONTRADICTED")
        self.assertIn("4", data["claims"][0]["best_evidence"])


if __name__ == "__main__":
    unittest.main()
