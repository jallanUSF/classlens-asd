# ClassLens ASD — Research Brief (for external LLM evaluation)

## What it is
ClassLens ASD is a solo-developer hackathon entry for the **Gemma 4 Good Hackathon** (Kaggle, deadline 2026-05-18). It's a multi-agent system that helps **special education teachers of autistic students** convert daily classroom work artifacts (handwritten worksheets, photos, tally sheets) into IEP-aligned progress data and personalized intervention materials. Dev is Jeff; content/validation partner is his wife Sarah (a classroom teacher). Judging is ~70% non-technical (story, impact, teacher-usability) and ~30% technical (real Gemma 4 capability use).

## Live stack (what's actually running, April 2026)
- **Backend:** Python 3.11 + FastAPI on uvicorn, port **8001** (8000 is taken by an unrelated process on the dev machine). Routers in `backend/routers/*` (students, capture, materials, chat, alerts, documents).
- **Frontend:** Next.js **16.2.2** (App Router, Turbopack) + Tailwind + shadcn/ui. `frontend/next.config.ts` rewrites `/api/*` to `http://localhost:8001`. All pages are client components (`"use client"`); no RSC data fetching.
- **Data:** Pydantic v2 models + JSON files in `data/`. No database. 7 synthetic student profiles in `data/students/`, 20 work artifacts in `data/sample_work/` with 1:1 precomputed JSONs in `data/precomputed/` so the demo never waits on live API for already-seen images. 2 mock IEP PDFs in `data/sample_iep/`.
- **Tests:** 71 pytest passing; `scripts/cold_boot_smoke.py` runs live HTTP against a real backend; `scripts/feature_smoke.py` runs TestClient against real Gemma for the 5 new features.
- **No LangChain, no LangGraph, no CrewAI** — direct API calls only. The client wrapper is `core/gemma_client.py`.

## Four-agent pipeline
Sequential, not autonomous: image in → structured data out → materials generated.
1. **Vision Reader** (`agents/vision_reader.py`) — Gemma multimodal OCR: student-work photo → structured JSON via function calling.
2. **IEP Mapper** (`agents/iep_mapper.py`) — maps transcribed work to the student's IEP goals, records trial data.
3. **Progress Analyst** (`agents/progress_analyst.py`) — thinking mode for trend detection, plateau/regression alerts.
4. **Material Forge** (`agents/material_forge.py`) — generates 7 output types for 3 audiences (teacher/parent/admin): lesson plan, tracking sheet, social story, visual schedule, first-then board, parent communication, admin report.

A fifth agent was just added: **IEP Extractor** (`agents/iep_extractor.py`) — renders IEP PDFs to PIL images via `pymupdf`, runs Gemma multimodal + function calling to extract `{student_name, grade, asd_level, communication_level, interests, iep_goals[], accommodations[]}` from real IEP documents. Wired into the `POST /api/documents/upload` endpoint and the Add Student flow.

## Model provider abstraction
`core/gemma_client.py::GemmaClient` supports three backends via `MODEL_PROVIDER` env var:
- **`google`** — Google AI Studio SDK, model `gemma-4-31b-it`. **Only provider with working function calling AND thinking mode** (`types.ThinkingConfig(includeThoughts=True)`).
- **`openrouter`** — OpenAI-compatible via OpenRouter, model `google/gemma-3-27b-it`. Function calling returns 404 on this endpoint (falls back to text-parse JSON extraction). Thinking mode unimplemented (returns empty).
- **`ollama`** — OpenAI-compatible via local Ollama. Models installed: `gemma4:e4b` (8B Q4), `gemma4:26b`. Function calling status unknown per-model. Thinking mode unimplemented.

The non-Google backends fall back to `_openai_generate` for thinking and return `{thinking: "", output: "..."}` — the fallback is architectural, not data.

## Features just shipped (still unstaged, awaiting commit)
1. **Real IEP PDF auto-extraction** — replaces a docstring lie. Gemma reads the PDF, returns structured goals + demographics, Add Student UI shows an "Extracted from IEP" card.
2. **Chat SSE streaming** — new `POST /api/chat/stream` with `StreamingResponse`, `useChat.ts` consumes via `fetch` + `ReadableStream` + `TextDecoder` (not `EventSource` — need POST with body).
3. **"Why is this an alert?" thinking trace UI** — new `POST /api/alerts/{id}/analyze` runs `ProgressAnalyst` via `generate_with_thinking`, `AlertBanner.tsx` reveals a collapsible panel showing Gemma's reasoning. **Only populates non-empty on `MODEL_PROVIDER=google`.**
4. **First-Then board** exposed in materials router (was orphaned).
5. **Bilingual parent communications** — language toggle (EN/ES/VI/ZH) in `MaterialViewer.tsx`, threaded through to the prompt template.

## Hardware constraint that drives the provider decision
Dev machine is **Windows Server 2022 headless, no GPU** (wmic reports only Microsoft Remote Display Adapter + Microsoft Basic Display Adapter). Ollama `gemma4:e4b` runs at **~5 tok/s** on CPU. Measured solo (no contention): chat TTFB 80s, IEP extraction 761s (12.7 min), alert analysis 558s (9.3 min), Spanish letter 451s (7.5 min), total ~30 min for 4 features. Google AI Studio does the same 4 in ~3 min. **Ollama is not viable for a live demo on this specific machine**, though it'd become competitive on any GPU box.

## Open decision this brief is for
Jeff needs the external LLM to evaluate: **given the above, what research or experimental angles should ClassLens pursue in the remaining ~5 weeks that would maximize judge appeal?** Specifically interested in ideas that:
- Exploit Gemma 4's headline features (multimodal, function calling, thinking mode, long context) in ways the current 5 features don't.
- Map to the "Gemma for Good" framing (equity, accessibility, special populations).
- Are implementable solo in a few days, not multi-week research projects.
- Don't require touching video/deploy/submission work (explicitly blocked — Jeff is gating that phase separately).

**Out of scope for the advisor:** model training/fine-tuning (no time), changing frameworks (Next.js + FastAPI is locked), anything requiring a GPU on the dev box.
