# HANDOFF.md — Session Summary

**Date:** 2026-04-05
**Session:** Sprint 6 — Next.js + FastAPI Redesign (Planning + Backend)
**Branch:** `nextjs-redesign` (branched from `master` at `b0f4763`)
**Next session:** Continue Sprint 1 (FastAPI) or start Sprint 2 (Next.js frontend)

## Goal
Replace Streamlit UI with Next.js frontend + FastAPI backend. Make Gemma 4 a visible conversational assistant throughout. Professional output rendering. Scale to dozens of students.

## What Got Done

### UX/UI Brainstorm (all validated with Jeff)
- **Mental model:** Student-anchored with smart alerts. Gemma 4 as expert IEP co-teacher.
- **Three-column layout:** Student sidebar (240px) | Content area (flex) | Chat panel (320px, prominent)
- **Class dashboard:** Greeting + alerts + recent activity (no charts — charts on student pages)
- **Student detail page:** Header → alerts → goals → recent work → materials → quick actions (scrollable)
- **Add Student flow:** Conversational via chat panel. Upload IEP PDF → Gemma extracts goals via multimodal + function calling. Profile builds in real-time.
- **Scan Work flow:** Conversational capture. Gemma explains what it sees, offers follow-ups, generates materials inline.
- **Professional outputs:** Purpose-built React renderers for each material type. Print CSS. No JSON visible to teachers.
- **Visual design system:** Calm classroom aesthetic. #4A7FA5 primary, Inter font, 12px radius, WCAG AA contrast, no pure red.

### Design Documents Written
- `docs/plans/2026-04-05-nextjs-redesign.md` — Full 13-section design doc
- `docs/plans/2026-04-05-implementation-plan.md` — 6-sprint implementation plan with 26 tasks

### FastAPI Backend Built (Sprint 1, Tasks 1-7)
- `backend/main.py` — FastAPI app with CORS, lifespan, 6 routers mounted
- `backend/routers/students.py` — Full CRUD: list, get, create, update, delete
- `backend/routers/capture.py` — Upload image + run existing pipeline, save document record
- `backend/routers/materials.py` — Generate materials via existing MaterialForge, save/list/approve
- `backend/routers/chat.py` — Chat endpoint with system prompt, student context injection, mock responses for dev
- `backend/routers/alerts.py` — Plateau/regression detection from trial data
- `backend/routers/documents.py` — IEP PDF upload (extraction stub — chat service handles)
- `backend/tests/test_students_api.py` — 10 tests covering all endpoints

### Test Status
- **45 tests total** (35 original + 10 new API tests), all passing
- No regressions to existing agent/pipeline tests

## What Worked
- Brainstorming one question at a time kept decisions focused and validated
- FastAPI wrapping existing code was fast — agents/pipeline/state_store unchanged
- Test-first approach caught a name mismatch immediately (Maya vs Maya Chen)

## What Didn't Work / Watch Out For
- Streamlit code is still in `app.py` and `ui/` — don't delete yet, useful as reference
- The `/api/chat` endpoint is synchronous with mock responses for now — needs SSE streaming + real model integration
- The `/api/documents/upload` endpoint saves files but doesn't extract content yet — the chat service will handle IEP extraction
- Alert IDs are random UUIDs regenerated each call — dismissed alerts won't persist across regenerations (needs fixing)

## Architecture Decision: OpenRouter
- Switching from Google AI Studio direct to OpenRouter for model access
- Single API key routes to Gemma 4 (and fallback models)
- Avoids 5-15 RPM rate limit on Google AI Studio free tier
- `GemmaClient` wrapper needs updating to support OpenRouter's OpenAI-compatible format
- Config: `MODEL_PROVIDER=openrouter|google|ollama` in `.env`

## Repo State
- **Branch:** `nextjs-redesign`
- **Tests:** 45/45 passing
- **Backend runs:** `uvicorn backend.main:app --reload --port 8000`

## Sprint Plan (from implementation plan)

| Sprint | Focus | Status |
|--------|-------|--------|
| Sprint 1 | FastAPI backend (7 tasks) | DONE |
| Sprint 2 | Next.js frontend — layout & shell (3 tasks) | NOT STARTED |
| Sprint 3 | Student detail page + chat integration (4 tasks) | NOT STARTED |
| Sprint 4 | Professional output rendering (4 tasks) | NOT STARTED |
| Sprint 5 | Polish + deploy (5 tasks) | NOT STARTED |
| Sprint 6 | Video + submission (3 tasks) | NOT STARTED |

## Next Steps
1. **Start Sprint 2:** `npx create-next-app@latest frontend --typescript --tailwind --app --src-dir`
2. Install shadcn/ui, configure Tailwind with our design tokens
3. Build three-column layout shell (sidebar + content + chat panel)
4. Wire sidebar to `GET /api/students` endpoint
5. Build class dashboard (greeting + alerts + activity timeline)

## Key Files for Next Session
- Design doc: `docs/plans/2026-04-05-nextjs-redesign.md`
- Implementation plan: `docs/plans/2026-04-05-implementation-plan.md`
- Backend entry: `backend/main.py`
- API tests: `backend/tests/test_students_api.py`
- Original pipeline (unchanged): `core/pipeline.py`
