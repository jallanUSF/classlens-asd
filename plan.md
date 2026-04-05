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

## Sprint 2: Next.js Frontend — Layout & Shell
- [ ] Scaffold Next.js + Tailwind + shadcn/ui
- [ ] Three-column layout (sidebar, content, chat panel)
- [ ] Design system: colors, typography, spacing
- [ ] Student sidebar wired to API
- [ ] Class dashboard (greeting + alerts + activity)

## Sprint 3: Student Detail + Chat
- [ ] Student page: header, goals, work, materials, quick actions
- [ ] Chat panel: streaming, context-aware, action cards
- [ ] Add Student flow (conversational via chat)

## Sprint 4: Professional Output Rendering
- [ ] Lesson plan, parent letter, admin report renderers
- [ ] Social story, tracking sheet, visual schedule renderers
- [ ] Print CSS + PDF export

## Sprint 5: Polish + Deploy
- [ ] Mobile responsive
- [ ] OpenRouter integration
- [ ] Vercel (frontend) + Railway (backend) deploy
- [ ] Precomputed demo data

## Sprint 6: Video + Submission
- [ ] Demo recording
- [ ] Video production
- [ ] Kaggle submission
