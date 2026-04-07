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

## Sprint 6: Video + Submission
**BLOCKED — not scheduled until Jeff explicitly approves release readiness.**
