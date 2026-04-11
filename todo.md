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

## QA Session Fix Queue (2026-04-11 very-late-night) — COMPLETE 2026-04-11
Full findings in `docs/qa-reports/qa-report-classlens-2026-04-11.md`. Was 66/100 health score, 12 findings. 8 of 12 resolved this session (all critical/high + two mediums + one low). 4 low-impact items deferred.

- [x] **Finding 7 — Dashboard AbortController regression**. Added `ac.signal.aborted` guard before setState in `frontend/src/app/page.tsx` matching the student-page pattern.
- [x] **Finding 11 — Spanish parent letter teacher-name placeholder**. Threaded `teacher_name` through `MATERIAL_FORGE_PARENT_COMM` prompt with explicit "write this exact name on the signature line" instruction. Default `Ms. Rodriguez` when student profile has no `teacher` field.
- [x] **Finding 6 — IEP extraction duplicates fields**. `agents/iep_extractor.py::_merge_pages` now dedupes goals by normalized 80-char description prefix (was keying on goal_id, which the model reassigns per page). Accommodations and interests dedupe on normalized full text. Verified: 5 raw goals → 3 unique, 4 accommodations → 3, 3 interests collapsed from 4.
- [x] **Finding 3 — Alert label classifier**. New `_classify_goal()` in `backend/routers/alerts.py` emits `declining | plateau_below | plateau_at_target` based on monotone trend + target comparison. Improving goals emit no alert. Titles, detail text, and suggested actions all branch per label. Verified: Amara G2 (45/42/40, target 70) → `declining`, Maya G1 (80/80/80, target 80) → `plateau_at_target`.
- [x] **Finding 2 — Alert ids deterministic**. `_stable_alert_id()` hashes `{student}_{goal}_{label}` with sha256, first 8 hex chars. Same alert → same id across fetches; no more 404s on analyze after the frontend caches an id.
- [x] **Finding 8 — Alert severity populated**. `high` for declining, `medium` for plateau_below, `low` for plateau_at_target. Rolled in with the classifier refactor.
- [x] **Finding 4 — `first_then` renderer**. New `frontend/src/components/materials/FirstThenView.tsx` parses the Material Forge markdown into FIRST / arrow / THEN / teacher-notes cards, with `react-markdown` rendering inside each section. Added to `MaterialViewer.tsx` switch and `TYPE_TITLES`.
- [x] **Finding 5 — Chat SSE whitespace concat**. `backend/routers/chat.py::_sanitize_stream_chunk` sanitizes HTML tags WITHOUT the trailing `.strip()` that was eating leading/trailing spaces from every Gemma chunk. `to40%` / `investedin` word-merge bug root cause was the `_sanitize_model_text().strip()` call inside the stream loop.
- [x] **Finding 1 — Stream every Gemma endpoint** (demo blocker). New `backend/routers/_sse.py::run_streaming_job` runs blocking Gemma calls in `asyncio.to_thread` with 4-second heartbeat frames so the Turbopack dev proxy keeps the socket open. Streaming variants added: `POST /api/alerts/{id}/analyze/stream`, `POST /api/materials/generate/stream`, `POST /api/documents/upload/stream`. Frontend consumers (`AlertBanner.tsx`, `MaterialViewer.tsx` language toggle, `student/new/page.tsx`) all switched via new shared `frontend/src/lib/sseJob.ts::consumeSseJob<T>` helper. Non-streaming originals retained for TestClient smokes.

## QA Session Low-Priority Follow-ups (deferred)
- [ ] Finding 9 — Chat send button `disabled` state doesn't react to programmatic `fill`. Harmless for humans; annoying for automation scripts.
- [ ] Finding 10 — `/sw.js` 404 on every page load. Either ship a minimal `public/sw.js` stub or remove the manifest reference.
- [ ] Finding 12 — Bilingual letters regenerate independently instead of translating the approved EN version. Consider translating in non-English languages to preserve student-specific color.

## Next session — live browser QA verification pass
- [ ] Real Chrome walk-through of all 4 previously-500 endpoints to confirm browser-path works end-to-end (not just TestClient):
  1. Click "Why?" on Amara G2 alert → should show heartbeat → thinking trace
  2. Upload `data/sample_iep/amara_iep_2025.pdf` in Add Student → should show heartbeat → 3 goals / 3+ accommodations
  3. MaterialViewer → open Maya parent letter → click ES → should regenerate with "Ms. Rodriguez" signature
  4. MaterialViewer → open Maya first_then draft → should render FIRST/THEN cards, not raw markdown dump
- [ ] Spot-check declining vs plateau_at_target vs plateau_below labels on dashboard

## Follow-up to decide
- [x] **DONE last session:** Switch `MODEL_PROVIDER=google`. Feature works end-to-end; QA confirmed the backend content quality is exceptional on Google AI Studio.

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
