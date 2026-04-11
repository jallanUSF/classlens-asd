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

## Synthetic Test Content Expansion (COMPLETE 2026-04-11)
- [x] 9 new work artifacts: Amara x2, Ethan x2, Lily x2, Marcus x2, Sofia x1
- [x] 2 alert-triggering scenarios (Amara G2 regression, Ethan G2 plateau)
- [x] All 7 students now have ≥1 sample work PNG + precomputed JSON
- [x] Windows font fallback in generate_sample_work.py (Arial / Segoe UI)
- [x] Pipeline cache-hit verified for all 9 new artifacts

## Judge-Appeal Features (2026-04-11 — no more lying code) — COMPLETE
- [x] #1: IEP PDF auto-extraction — new `agents/iep_extractor.py` + pymupdf PDF→PNG rendering + Gemma multimodal function calling, wired into `/api/documents/upload` and the Add Student UI (shows "Extracted from IEP" card)
- [x] #2: Chat SSE streaming — new `POST /api/chat/stream` with `StreamingResponse`, `useChat.ts` rewritten to consume via fetch + ReadableStream + TextDecoder
- [x] #3: Thinking-trace UI — new `POST /api/alerts/{id}/analyze` runs ProgressAnalyst via `generate_with_thinking`, `AlertBanner.tsx` has a "Why?" button that reveals a collapsible reasoning panel
- [x] #4: Exposed first_then in materials.py enum + router handler
- [x] #5: Bilingual parent comms — `language` param threaded from MaterialViewer toggle (EN/ES/VI/ZH) through router → MaterialForge → prompt template

## Follow-up to decide
- [ ] Consider switching `MODEL_PROVIDER=google` (Google AI Studio) — on OpenRouter, `google/gemma-3-27b-it` returns 404 for tool use, so every function-calling agent falls back to text-parse JSON extraction. Google AI Studio supports real function calling AND non-empty thinking traces. Fully within existing infra (`gemma_client.py` has both backends ready).

## Sarah Content Review (IN PROGRESS)
- [x] Build `sarah_review_bundle/` (7 student dockets + 12 sample outputs across all material types)
- [ ] Share bundle with Sarah and collect feedback
- [ ] Apply Sarah's feedback to prompt templates / student profiles as needed

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
