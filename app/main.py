"""
FastAPI application entry point.

Start the server with:
    uvicorn app.main:app --reload --port 8000

Or from the backend/ directory:
    python -m uvicorn app.main:app --reload --port 8000
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

# ─── Load environment variables ───────────────────────────────────────────────

# Load from backend/.env if it exists
_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()   # fallback: look in cwd

# ─── App instance ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Codebase Analyzer API",
    description=(
        "Analyzes local Git repositories: extracts file dependency graphs, "
        "calculates complexity metrics, and generates AI-powered file summaries."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ─── CORS ────────────────────────────────────────────────────────────────────
# Allow the React dev server (Vite default: 5173) and any other local origins.
# In production you'd lock this down to your actual domain.
# Configure via CORS_ORIGINS environment variable (comma-separated)

_default_origins = [
    "http://localhost:5173",    # Vite dev server
    "http://localhost:3000",    # CRA fallback
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

_cors_env = os.getenv("CORS_ORIGINS", "")
if _cors_env:
    _allowed_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
else:
    _allowed_origins = _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(router, prefix="/api")

# ─── Root ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["meta"])
def root():
    return {
        "message": "Codebase Analyzer API",
        "docs": "/docs",
        "health": "/api/health",
    }
