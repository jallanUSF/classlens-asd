"""
ClassLens ASD — FastAPI Backend
Wraps existing Python agents with REST API endpoints.
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path so we can import core/, agents/, schemas/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.routers import students, capture, materials, chat, alerts, documents, trajectory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure data directories exist on startup."""
    data_dir = PROJECT_ROOT / "data"
    for subdir in ["students", "documents", "materials", "alerts", "conversations", "precomputed", "flags"]:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="ClassLens ASD API",
    description="Multimodal IEP Intelligence for Autistic Learners",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS — allow Next.js dev server and explicitly configured production origins.
# CORS_ORIGINS: comma-separated exact origins (preferred for prod).
# CORS_ORIGIN_REGEX: optional regex (e.g. to allow all *.vercel.app preview URLs).
# Leave CORS_ORIGIN_REGEX unset in production unless you really want a wildcard.
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_env_origins = os.environ.get("CORS_ORIGINS", "")
_cors_origins = [o.strip() for o in _env_origins.split(",") if o.strip()] if _env_origins else _default_origins
_cors_origin_regex = os.environ.get("CORS_ORIGIN_REGEX") or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Mount routers
app.include_router(students.router, prefix="/api")
app.include_router(capture.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(trajectory.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.3.0"}
