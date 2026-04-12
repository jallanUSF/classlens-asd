# Next.js + FastAPI Redesign Plan

## Goal
Replace Streamlit with Next.js frontend + FastAPI backend. Gemma 4 as visible conversational assistant. Professional outputs.

Full design: `docs/plans/2026-04-05-nextjs-redesign.md`
Full implementation: `docs/plans/2026-04-05-implementation-plan.md`

## Sprint 1: FastAPI Backend ✅
- [x] Project scaffold + dependencies
- [x] Student CRUD endpoints (list, get, create, update, delete)
- [x] Capture endpoint (pipeline integration)
- [x] Materials generation endpoint
- [x] Chat endpoint (mock responses, context-aware)
- [x] Alerts endpoint (plateau/regression detection)
- [x] Documents upload endpoint
- [x] 10 API tests passing

## Sprint 2: Next.js Frontend — Layout & Shell ✅
- [x] Scaffold Next.js + Tailwind + shadcn/ui
- [x] Three-column layout (sidebar, content, chat panel)
- [x] Design system: colors, typography, spacing
- [x] Student sidebar wired to API
- [x] Class dashboard (greeting + alerts + activity)

## Sprint 3: Student Detail + Chat ✅
- [x] Student page: expandable goals with Plotly charts, alert banner
- [x] Recent work timeline + materials library + quick actions
- [x] Chat panel: useChat hook, ChatMessage, ActionCard, context-aware
- [x] Add Student flow (conversational via chat, profile preview, IEP upload)

## Sprint 4: Professional Output Rendering ✅
- [x] Lesson plan, parent letter, admin report renderers
- [x] Social story, tracking sheet, visual schedule renderers
- [x] MaterialViewer sheet + approve/regenerate controls
- [x] Print CSS (hides chrome, letter-size, clean layout)

## Sprint 5: Polish + Deploy ✅
- [x] Mobile responsive (hamburger + FAB + overlays)
- [x] OpenRouter integration (google/openrouter/ollama toggle)
- [x] Deploy config (Vercel + Railway/Render + CORS + env vars)
- [x] Precomputed demo data (9 materials + 3 alerts)
- [x] Competition assets updated (video script, writeup, ADR)

## Acceleration Sprint: Prize Track Features (Apr 12–May 9)

### Feature 1 — Long-context trajectory report ✅
**Prize:** Main track + Future of Education | **Gemma 4:** 256K context
- [x] `agents/trajectory_analyst.py` — aggregate all trial data + alerts into one Gemma 31B call with thinking mode
- [x] `backend/routers/trajectory.py` — `POST /api/students/{id}/trajectory` + SSE stream
- [x] `TrajectoryReport.tsx` — per-goal status badges (On Track / At Risk / Stalled / Met), trend summary, IEP meeting note, cross-goal patterns, thinking trace
- [x] Precomputed results for Maya, Amara, Jaylen
- [x] 11 tests

### Feature 3 — Voice note capture ✅
**Prize:** Digital Equity + Future of Education | **Gemma 4:** Audio (E4B)
- [x] `agents/voice_reader.py` — audio → structured trial data via Gemma (+ text fallback)
- [x] `POST /api/capture/voice` + stream endpoints in capture router
- [x] `VoiceCapture.tsx` — MediaRecorder + base64 + preview + text fallback mode
- [x] Provider guard: non-google returns text_input fallback
- [x] `GET /api/capture/voice/supported` — runtime capability check
- [x] 9 tests

### Feature 4 — Confidence panel ✅
**Prize:** Safety & Trust ($10K) | **Gemma 4:** Thinking mode extended
- [x] `agents/material_forge.py` — all generate calls use `generate_with_thinking()`, `_compute_confidence()` scorer
- [x] confidence_score + thinking in material record, extracted from content
- [x] `MaterialViewer.tsx` — confidence badge + collapsible reasoning panel + Flag for Review button
- [x] `POST /api/materials/{student_id}/{material_id}/flag` endpoint → `data/flags/`
- [x] 9 tests, 24 existing materials migrated

## Sprint 6: Video + Submission
**BLOCKED — not scheduled until Jeff explicitly approves release readiness.**
