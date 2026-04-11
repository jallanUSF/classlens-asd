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

## QA Session Fix Queue (2026-04-11 very-late-night) — ordered fastest → biggest
Full findings in `docs/qa-reports/qa-report-classlens-2026-04-11.md`. 66/100 health score. 12 findings.

- [ ] **Finding 7 — Dashboard AbortController regression** (~10 min). Add the controller to `frontend/src/app/page.tsx` that HANDOFF claimed shipped last session but didn't. Verify the first fetch shows `ERR_ABORTED` in the Network panel.
- [ ] **Finding 11 — Spanish parent letter teacher-name placeholder** (~10 min). Thread `{teacher_name}` into the ES prompt branch in `prompts/templates.py`. Compare cached EN vs regenerated ES for the same student.
- [ ] **Finding 6 — IEP extraction duplicates fields** (~15 min). In `agents/iep_extractor.py`, dedupe the pages 1+2 merge on goal description / accommodation string. Test with `data/sample_iep/amara_iep_2025.pdf` — should be 3 goals, 6 accommodations.
- [ ] **Finding 3 — Alert label classifier collapses 3 outcomes into "plateaued"** (~20 min). `backend/routers/alerts.py` should emit one of `declining | plateau_below | plateau_at_target | improving`. The Progress Analyst already computes this inside thinking mode — surface it. Fix Amara (declining) and Maya G1 (target met).
- [ ] **Finding 2 — Alert ids non-deterministic** (~20 min). Derive ids as a hash of `{student_id}_{goal_id}_{week_window}` so the same alert always gets the same id. Unblocks retries.
- [ ] **Finding 4 — `first_then` has no renderer** (~30 min). New `frontend/src/components/materials/FirstThenView.tsx` with FIRST / arrow / THEN box layout. Add to `MaterialViewer.tsx` switch. Content is already excellent — just needs the component.
- [ ] **Finding 5 — Chat SSE whitespace concat** (~30 min). `frontend/src/hooks/useChat.ts` token reducer is dropping leading/trailing spaces between SSE delta frames OR the markdown renderer collapses whitespace. Repro by asking Amara's page about G2 interventions and looking for `to40%`, `investedin`, `Notepad"with`.
- [ ] **Finding 1 — Next.js dev proxy kills long Gemma calls** (~2-3h, demo blocker). Stream every Gemma endpoint like `/api/chat/stream` does. Mirror the SSE pattern in `backend/routers/alerts.py::analyze`, `backend/routers/documents.py::upload`, `backend/routers/materials.py::generate`. Frontend consumers need the same `fetch` + `ReadableStream` + `TextDecoder` wiring `useChat.ts` has. Bonus: watching reasoning unfold live is a better demo than a 40s spinner.

## QA Session Low-Priority Follow-ups
- [ ] Finding 8 — Populate alert `severity` field (was `null` for all alerts). Low impact until the UI actually sorts/colors by severity.
- [ ] Finding 9 — Chat send button `disabled` state doesn't react to programmatic `fill`. Harmless for humans; annoying for automation scripts.
- [ ] Finding 10 — `/sw.js` 404 on every page load. Either ship a minimal `public/sw.js` stub or remove the manifest reference.
- [ ] Finding 12 — Bilingual letters regenerate independently instead of translating the approved EN version. Consider translating in non-English languages to preserve student-specific color.

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
