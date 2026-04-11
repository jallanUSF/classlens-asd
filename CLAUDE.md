# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is
ClassLens ASD is a hackathon entry for the Gemma 4 Good Hackathon (Kaggle, deadline May 18 2026). A multi-agent system that helps special education teachers of autistic students convert daily classroom work artifacts into IEP-aligned progress data and personalized intervention materials.

## Competition Goal
WIN. This is not production software. It's a demo that needs to:
1. Work end-to-end for a 3-minute video demo
2. Have a live public URL judges can try
3. Show real Gemma 4 usage (multimodal, function calling, thinking mode)
4. Tell a compelling human story (70% of score is non-technical)

## Tech Stack Context

### Current (active development — nextjs-redesign branch)
- **Model:** Google Gemma 4 via OpenRouter (`google/gemma-3-27b-it`) through the shared `core/gemma_client.py` OpenAI-compatible client. Also supports Google AI Studio (`google.genai`) and local Ollama.
- **Backend:** Python 3.11+ with FastAPI, served by uvicorn on **port 8001** (canonical — port 8000 conflicts with an unrelated process on the dev machine)
- **Frontend:** Next.js 16 (App Router) + Tailwind + shadcn/ui. Rewrites `/api/*` to the FastAPI backend (default `API_URL=http://localhost:8001`)
- **Charts:** Plotly in the dashboard
- **Data:** Pydantic v2 models + JSON files in `data/` (no database)
- **NO LangChain, NO LangGraph, NO CrewAI** — direct API calls only

### Future (Kaggle submission form factor — triggered only by Jeff's explicit approval)
- **Framework:** Streamlit + Streamlit Community Cloud (stub code already lives under `ui/` and `app.py` from the pre-redesign era)
- Do NOT touch Streamlit code or Kaggle submission artifacts until Jeff releases the gate. The current Next.js + FastAPI stack is what we run and test against.

## Commands
```bash
# Install (Python)
pip install -r requirements.txt

# Install (frontend)
cd frontend && npm install

# Run backend (canonical port 8001)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001

# Run frontend (in a second terminal)
cd frontend && npm run dev

# Run tests (pytest with fixtures in tests/conftest.py)
python -m pytest tests/ -q
python -m pytest tests/test_backend_security.py -v   # security + sanitization suite

# Live end-to-end smoke test (requires backend running on 8001)
python scripts/cold_boot_smoke.py

# Offline pipeline smoke test (no backend needed)
python scripts/test_pipeline.py

# Test Gemma API access
python -c "from core.gemma_client import GemmaClient; c = GemmaClient(); print(c.generate('Hello'))"

# Frontend build
cd frontend && npx next build
```

Environment: copy `.env.example` to `.env`, set `MODEL_PROVIDER=openrouter` and `OPENROUTER_API_KEY=...` (or `GOOGLE_AI_STUDIO_KEY=...` if using Google AI Studio). Frontend reads `API_URL` from `frontend/.env.local` (defaults to `http://localhost:8001`).

## Architecture

### Four-Agent Pipeline
The pipeline runs sequentially: image in → structured data out → materials generated.

1. **Vision Reader** (`agents/vision_reader.py`) — Gemma 4 multimodal OCR: photo of student work → structured JSON transcription via function calling
2. **IEP Mapper** (`agents/iep_mapper.py`) — Function calling: maps transcribed work to student's IEP goals, records trial data
3. **Progress Analyst** (`agents/progress_analyst.py`) — Thinking mode: trend detection, progress notes, regression alerts
4. **Material Forge** (`agents/material_forge.py`) — Generates 7 output types for 3 audiences (teacher, parents, admin)

### Data Flow
- `core/gemma_client.py` — Single API wrapper for all Gemma 4 interactions (text, vision, function calling, thinking mode)
- `core/pipeline.py` — End-to-end orchestration wiring the 4 agents together
- `core/state_store.py` — CRUD for student JSON profiles in `data/students/`
- `schemas/student_profile.py` — Pydantic v2 models: `StudentProfile`, `IEPGoal`, `TrialData`, `SensoryProfile`
- `schemas/tools.py` — JSON schemas for Gemma 4 function calling declarations
- `prompts/templates.py` — All system and user prompt templates (use `.format()` placeholders)
- `data/precomputed/` — Cached demo results so the demo NEVER waits for API

### Test Infrastructure
- `tests/conftest.py` — Shared pytest fixtures: `mock_client`, `state_store` (temp dir), per-student profile fixtures (`maya_profile`, `jaylen_profile`, `sofia_profile`)
- `tests/mock_api_responses.py` — `MockGemmaClient`: drop-in replacement for `GemmaClient` for offline dev
- `tests/gold_standard_outputs.json` — Expected outputs for validation

### Sample Data
Seven demo students in `data/students/`. Core three: `maya_2026.json` (Grade 3, Level 2), `jaylen_2026.json` (Grade 1, Level 3, non-verbal), `sofia_2026.json` (Grade 5, Level 1). Four additional: `amara`, `ethan`, `lily`, `marcus`. Sample work images in `data/sample_work/` — all seven have matching precomputed JSONs in `data/precomputed/` so the demo never waits on a live API call.

### UI Layer
- **Active:** `frontend/` — Next.js 16 App Router, calls the FastAPI backend via `/api/*` rewrites (default `API_URL=http://localhost:8001`)
- **Dormant (Kaggle-only):** `ui/` Streamlit stub and `app.py` — do not touch until Jeff approves the release gate and we transition to the Kaggle submission form factor

## Critical Rules
1. **Pre-baked demo mode:** All sample images have pre-computed results cached. Demo NEVER waits for API.
2. **Function calling fallback:** Every agent must have `_parse_fallback()` to extract JSON from text if Gemma tool calls fail.
3. **Teacher-in-the-loop:** All outputs have approve/edit/regenerate UI. Nothing auto-sends.
4. **ASD-friendly design:** Predictable layouts, calm colors (`#5B8FB9` primary, `#FAFAFA` bg), concrete vocabulary, no surprises.

## Key Reference Docs
- `docs/planning/IMPLEMENTATION-PLAN.md` — Day-by-day build order (the "build bible")
- `docs/wireframe.html` — Open in browser for visual UI spec
- `docs/UX-COPY-REFERENCE.md` — All UI strings ready to paste into Streamlit
- `docs/ACCESSIBILITY-AUDIT.md` — ASD-friendly CSS snippets
- `docs/ADR.md` — Architecture decisions (for judges)
- `docs/VIDEO-SCRIPT.md` — 3-min video script (build demo around this)
- `docs/COMPETITION-WRITEUP.md` — Kaggle submission draft
- `docs/SECURITY-REVIEW.md` — FERPA/privacy review

## Team
- **Jeff:** All code, architecture, deployment, video production
- **Sarah (wife, teacher):** Student profiles, work artifacts, output validation, video segments
