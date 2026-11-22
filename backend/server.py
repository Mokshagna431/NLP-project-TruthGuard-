"""
TruthGuard Server Entry Point (Delegates to backend.app.main:app)
"""

import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.main import app

if __name__ == "__main__":
    import uvicorn
    print("Starting TruthGuard Full-Stack Backend...")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
