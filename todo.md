# TODO — Next.js Redesign

- [x] Sprint 2: Scaffold Next.js + Tailwind + shadcn/ui + 3-column layout
- [x] Sprint 2: Wire student sidebar to GET /api/students
- [x] Sprint 2: Build class dashboard (alerts + activity) + student detail page
- [x] Sprint 3: Chat panel streaming integration (SSE + real API)
- [x] Sprint 3: Enhanced student detail (expandable goals, Plotly charts, alerts)
- [x] Sprint 3: Recent work timeline + materials library + quick actions
- [x] Sprint 3: Add Student conversational flow
- [x] Sprint 4: Professional material renderers (6 types + MaterialViewer sheet)
- [x] Sprint 4: Print CSS + approve/regenerate controls
- [x] Sprint 5: Mobile responsive layout (hamburger + FAB)
- [x] Sprint 5: OpenRouter integration + deployment config
- [x] Design review + polish passes (all findings resolved)
- [x] Sprint 5 finalization: real API wiring + image upload pipeline

## Path B — Hardening Week (COMPLETE)
- [x] Fill missing precomputed JSONs + fix Maya copy-paste bugs in 3 existing files
- [x] Security pass: filename sanitization, student_id validation, upload size/extension limits
- [x] CORS hardening (opt-in regex, explicit method/header allowlist)
- [x] HTML sanitization rewrite (script/style blocks + any-tag)
- [x] Unit tests for new security code (32 tests added)
- [x] Live cold-boot smoke test script (8/8 checks — real OpenRouter round-trip)
- [x] MISTAKES.md seeded
- [x] Port 8001 canonical (frontend default, docs, run instructions)
- [x] Synthetic test content (4 new work PNGs + 2 mock IEP PDFs)

## Live Browser QA Fixes (COMPLETE)
- [x] Fix G3 count-based goal display (Target: ≤1/day instead of 1%)
- [x] AbortController on 5 useEffect fetches (half the dev traffic, clean prod)
- [x] Scope chat history per student (reset on student switch)
- [x] Fix latent stale-state bug in student page context message
- [x] Gitignore data/documents/ (runtime upload state)

## Release Gate — RE-OPEN for Jeff
- [ ] Jeff approval for release readiness

## Jeff Open Questions (before Sprint 6 can start)
- [ ] Confirm Sarah's content status (profiles + video segments)
- [ ] Define "release ready" criterion (demo-ready vs. production-ready)

## Sprint 6 — Blocked on release gate
- [ ] Deploy target finalization
- [ ] 3-min video recording (against docs/VIDEO-SCRIPT.md)
- [ ] docs/COMPETITION-WRITEUP.md finalization
- [ ] Kaggle submission package (eventual transition to Streamlit form factor)
- [ ] Submit with 48h buffer before 2026-05-18
