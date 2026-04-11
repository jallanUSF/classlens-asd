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
- [x] Sprint 5 finalization: real API wiring + image upload pipeline (commit 783d355)

## Path B — Hardening Week (COMPLETE)
- [x] Fill missing precomputed JSONs (jaylen_pecs_log, maya_visual_schedule, sofia_transition_log)
- [x] Fix Maya copy-paste bugs in 3 existing precomputed JSONs (wrong goal_ids, identical Maya narratives)
- [x] Security pass: filename sanitization, student_id validation, upload size/extension limits
- [x] CORS hardening (opt-in regex, explicit method/header allowlist)
- [x] Stray-HTML sanitization rewrite (script/style blocks + any-tag regex)
- [x] Unit tests for new security code (32 tests added — 67/67 total pass)
- [x] Live cold-boot smoke test script + verified 7/7 end-to-end checks pass
- [x] MISTAKES.md seeded with 4 lessons from Sprints 1–5

## Release Gate (RE-OPENED — Jeff to decide)
- [ ] Jeff approval for release readiness after Path B hardening

## Jeff Open Questions (needed before Sprint 6 can start)
- [x] Resolve port 8000 conflict (8001 is now canonical for this project)
- [ ] Confirm Sarah's content status (profiles + video segments)
- [ ] Confirm deploy target (local + OpenRouter vs. other)
- [ ] Clarify "release ready" — demo-ready or production-ready?
