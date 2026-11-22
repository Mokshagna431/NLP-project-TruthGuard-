# TruthGuard 3.0: Installation & Deployment Guide

## 1. System Requirements

- **Operating System**: Windows 10/11 (64-bit), Ubuntu 20.04/22.04 LTS, or macOS 12+
- **Python**: Python 3.10 or 3.11 (tested on Python 3.11.9)
- **Node.js**: Node.js v18.0+ and npm v9.0+
- **Hardware**: Minimum 8 GB RAM (16 GB recommended), multi-core CPU. NVIDIA GPU optional (accelerates inference via PyTorch CUDA).

---

## 2. Quick-Start Commands (Windows)

The platform includes one-click launch scripts:

```powershell
# 1. Start the FastAPI REST Backend (Port 8000)
.\run_backend.bat

# 2. Start the React 19 Frontend (Port 5173)
.\run_frontend.bat
```

Once running, navigate to:
- **Interactive UI**: `http://localhost:5173`
- **Swagger API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

---

## 3. Manual Step-by-Step Installation

### Step 1: Clone or Open Workspace
```bash
cd "C:\College projects\NLP"
```

### Step 2: Set Up Python Environment & Dependencies
```bash
# Verify Python 3.11
python --version

# Install required Python packages
pip install -r requirements.txt

# Download spaCy English syntactic pipeline
python -m spacy download en_core_web_sm
```

### Step 3: Set Up React Frontend
```bash
cd frontend
npm install
npm run build
```

### Step 4: Run Platform Tests
```bash
# Run all unit, integration, and E2E regression tests (42 tests)
python -m unittest discover -s tests -p "test_*.py"
```

---

## 4. Environment Variables Configuration (`.env`)

Create a `.env` file in the project root:
```env
# Application Settings
APP_NAME=TruthGuard
APP_ENV=production
SECRET_KEY=truthguard_super_secret_jwt_key_2026_production
PORT=8000

# Database Connection (Defaults to local SQLite if omitted)
DATABASE_URL=sqlite:///./truthguard.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/truthguard

# Model Settings
NLI_MODEL=MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli
DENSE_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# API Timeouts
CROSSREF_TIMEOUT=3.0
SEMANTIC_SCHOLAR_TIMEOUT=3.0
```

---

## 5. Docker Deployment (Optional)

Run the entire platform via Docker Compose:
```bash
docker-compose up --build -d
```
