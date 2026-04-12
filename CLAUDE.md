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
- **Model:** Google Gemma 4 via **Google AI Studio** (`gemma-4-31b-it`) through the shared `core/gemma_client.py` `google.genai` client. This is the canonical provider — only one with working native function calling AND thinking mode (`types.ThinkingConfig(includeThoughts=True)`). OpenRouter (`google/gemma-3-27b-it`) and local Ollama (`gemma4:e4b`, `gemma4:26b`) are supported as fallbacks but have architectural gaps: OpenRouter returns 404 for tool use and forces the text-parse fallback path; Ollama has no `generate_with_thinking` code path (returns empty thinking) and on a GPU-less machine runs at ~5 tok/s CPU which is demo-unusable. See `scripts/provider_ab.py` for the A/B data.
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

Environment: copy `.env.example` to `.env`, set `MODEL_PROVIDER=google` and `GOOGLE_AI_STUDIO_KEY=...` (canonical). `OPENROUTER_API_KEY` and Ollama are supported as fallbacks — see `core/gemma_client.py` for provider init. Frontend reads `API_URL` from `frontend/.env.local` (defaults to `http://localhost:8001`).

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
- `core/json_io.py` — **UTF-8 safe JSON file I/O**. Every caller that reads or writes a student profile MUST route through `read_json` / `write_json` here. They enforce `encoding="utf-8"` + `ensure_ascii=False` + `indent=2`, which prevents the Windows cp1252 mojibake bug documented in MISTAKES.md #6. Never call `open()` on a JSON file without `encoding="utf-8"`.
- `schemas/student_profile.py` — Pydantic v2 models: `StudentProfile`, `IEPGoal`, `TrialData`, `SensoryProfile`
- `schemas/tools.py` — JSON schemas for Gemma 4 function calling declarations
- `prompts/templates.py` — All system and user prompt templates (use `.format()` placeholders)
- `data/precomputed/` — Cached demo results so the demo NEVER waits for API

### Test Infrastructure
- `tests/conftest.py` — Shared pytest fixtures: `mock_client`, `state_store` (temp dir), per-student profile fixtures (`maya_profile`, `jaylen_profile`, `sofia_profile`)
- `tests/mock_api_responses.py` — `MockGemmaClient`: drop-in replacement for `GemmaClient` for offline dev
- `tests/gold_standard_outputs.json` — Expected outputs for validation

### Sample Data
Seven demo students in `data/students/`. Core three: `maya_2026.json` (Grade 3, Level 2), `jaylen_2026.json` (Grade 1, Level 3, non-verbal), `sofia_2026.json` (Grade 5, Level 1). Four additional: `amara` (Grade 6, L1, inference/social regression), `ethan` (Grade 2, L2, echolalic, handwriting plateau), `lily` (Grade 4, L1, pragmatic language + coping), `marcus` (K, L3, AAC + playground). **20 work artifacts** in `data/sample_work/` with 1:1 precomputed JSONs in `data/precomputed/` — every student has ≥1 artifact and the demo never waits on live API. Two artifacts deliberately surface alert scenarios for Progress Analyst demo value: `amara_social_tracker` (5-week decline below baseline) and `ethan_handwriting_probe` (4-session plateau, intervention saturation). Regenerate with `python scripts/generate_sample_work.py` (or `--extended` for the 9 newest only).

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

## Acceleration Sprint (Apr 12–May 9)

### Feature 1 — trajectory_analyst.py
- New file at `agents/trajectory_analyst.py`
- New router at `backend/routers/trajectory.py`, mount at `/api/students/{id}/trajectory`
- Aggregates all trial data + alert history for one student into a single long-context Gemma call
- Single Gemma call: `gemma-4-31b-it`, `thinking=True`, long context (256K)
- Output schema: `{ goals: [{ goal_id, status, trend_summary, confidence, iep_meeting_note }] }`
- Add precomputed result to `data/precomputed/trajectory_{student_id}.json`

### Feature 3 — voice_reader.py
- New file at `agents/voice_reader.py`
- New endpoint at `backend/routers/capture.py`: `POST /api/capture/voice`
- Output schema: identical to vision_reader output (IEP Mapper receives same input either way)
- Provider guard: if `MODEL_PROVIDER != 'google'`, return `{"error": "audio_not_supported", "fallback": "text_input"}`
- Frontend: `VoiceCapture.tsx` — MediaRecorder + base64 encoding + review step before submit
- Sample assets: `data/sample_voice/` (Sarah records these, or synthetic)

### Feature 4 — confidence panel
- Modify `agents/material_forge.py`: all `generate()` calls → `generate_with_thinking()`
- Add `confidence_score` to MaterialOutput schema: `Literal["high", "review_recommended", "flag_for_expert"]`
- Confidence logic: `high` if student has >5 prior trials AND thinking trace has no hedge terms
- Frontend: extend `MaterialViewer.tsx` — copy `AlertBanner.tsx` thinking trace panel pattern
- New endpoint: `POST /api/materials/{id}/flag` → appends to `data/students/{id}/flags.json`

## Team
- **Jeff:** All code, architecture, deployment, video production
- **Sarah (wife, teacher):** Student profiles, work artifacts, output validation, video segments
