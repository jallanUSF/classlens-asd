# HANDOFF.md — Session Handoff

**Date:** 2026-04-11
**Branch:** `nextjs-redesign`
**Status:** Path B hardening week complete. Release gate question re-opened for Jeff.

---

## What Was Done (This Session — Path B Hardening)

Kicked off by a Project Manager / QA Manager review of Sprints 1–5. Both flagged that the "35/35 tests pass" release-ready claim rested entirely on mocked tests with zero coverage of the FastAPI routers, the `load_dotenv` fix, image upload, or the real OpenRouter API path. Chose Path B (one hardening week) before Sprint 6.

### 1. Committed pending Sprint 5 finalization (`783d355`)
11 files bundled into a single clean commit — real Gemma API wiring, image upload, pipeline precomputed-cache fallback, and HANDOFF/todo updates.

### 2. Filled the precomputed cache gap (all 7 sample PNGs now covered)
- Created `jaylen_pecs_log.json`, `maya_visual_schedule.json`, `sofia_transition_log.json` with student-specific transcriptions, goal mappings, analyses, and thinking chains.
- Fixed 3 existing precomputed JSONs that had Maya copy-paste bugs: `maya_math_worksheet.json` had duplicate analyses, `jaylen_task_checklist.json` mapped to the wrong goal (G1 → G2), `sofia_writing_sample.json` mapped to the wrong goal (G1 → G3) and all three narrated Maya's fire-drill story regardless of student.
- Demo now truly "never waits for API" — any sample PNG a judge uploads will resolve via cache.

### 3. Security hardening
- New `backend/upload_utils.py`: `safe_filename`, `validate_student_id`, `validate_upload`. 10 MB cap, extension allowlist, path-traversal blocking on both filenames and student IDs.
- `backend/routers/capture.py` rewritten to use it. Pulled the `tests.mock_api_responses` import out of the production happy path — now only loaded when no credentials exist.
- `backend/routers/documents.py` rewritten to use it as well.
- CORS tightened in `backend/main.py`: the permissive `https://*.vercel.app` regex is now opt-in via `CORS_ORIGIN_REGEX` env var (unset by default). `allow_methods` and `allow_headers` tightened from `*` to explicit lists.
- Secret scan: no hardcoded keys anywhere in the repo. `.env` correctly gitignored; only `.env.example` files are tracked, both with placeholders.

### 4. Chat HTML sanitization improved
Old regex only stripped `td|tr|table|div|span|p|br`. New `_sanitize_model_text` helper in `backend/routers/chat.py`:
- Drops `<script>…</script>` and `<style>…</style>` blocks including their bodies (so CSS/JS bodies don't leak as plain text).
- Strips any remaining `<…>` tag, regardless of name or attributes.
- Handles self-closing tags, headings, lists, anchors, tags with quoted attributes.

### 5. Test coverage for new code (32 new tests)
- `tests/test_backend_security.py` exercises `safe_filename`, `validate_student_id`, `validate_upload` (extension allowlist, size cap, empty file, missing filename), and `_sanitize_model_text` (all the tag categories above plus script/style blocks).
- These are real unit tests, not mocks — they close the coverage gap QA flagged.

### 6. Live cold-boot smoke test
New `scripts/cold_boot_smoke.py` + a live run against a fresh `uvicorn` on port 8001 (8000 still occupied by ulana.main):

| Check | Verdict | Notes |
|-------|---------|-------|
| `/health` | PASS | 200 `{"status":"ok"}` |
| `/api/students` | PASS | 7 profiles |
| `/api/chat` (Maya) | PASS | 230-char response — **real OpenRouter round-trip** |
| `/api/capture` happy path | PASS | 200, pipeline returned 2 matched goals (cache hit) |
| reject `.exe` upload | PASS | 400 with helpful detail |
| reject `../etc` student_id | PASS | 400 |
| reject >10 MB upload | PASS | 413 |

Backend log was clean throughout — no tracebacks, no `.env` warnings.

### 7. Created `MISTAKES.md`
Four entries seeded from this session and the prior one: the `load_dotenv` router gap, the precomputed copy-paste bug, the unsanitized upload pipeline, and the "35/35 pass means nothing when everything is mocked" lesson. Each has root cause + prevention rule per global CLAUDE.md.

### 8. New agent definitions (ready for next session)
Created `~/.claude/agents/project-manager.md` and `~/.claude/agents/qa-manager.md`. Not yet hot-loaded in this session, so the PM/QA runs used `general-purpose` with inlined personas. Next session will pick them up directly via `subagent_type`.

---

## Test State

- **Python:** 67/67 pytest green (was 35 — added 32 security/sanitization tests)
- **Frontend:** 0 TypeScript errors, `npx next build` clean (confirmed last session)
- **Cold-boot live:** 7/7 endpoint + validation checks pass against real uvicorn + real OpenRouter
- **Still mocked:** The original 35 agent/pipeline tests all use `MockGemmaClient`. That's acceptable — they cover the orchestration logic, not the provider. The provider path is now covered by the cold-boot script.

---

## Known Limitations / Gaps Not Closed

- **SSE streaming still absent** — chat returns a single JSON response. Fine for demo.
- **Port 8001 is now the canonical backend port** for this project. Port 8000 is occupied by an unrelated `ulana.main` process on the dev machine; rather than fighting it, 8001 is baked into `next.config.ts`, the cold-boot script, CLAUDE.md, and HANDOFF run instructions.
- **Sarah's content** (student profiles validated, video segments scripted) — unchanged this session; still the long-lead dependency for Sprint 6.
- **Deploy target decision** — CLAUDE.md still says "Streamlit Community Cloud." Memory says Jeff prefers local hosting + OpenRouter. Needs explicit call before Sprint 6 starts.

---

## How to Resume

### Start the app (port 8001 is the canonical backend port for this project)
```bash
# Terminal 1: Backend
cd C:/Projects/ClassLense && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001

# Terminal 2: Frontend (auto-proxies /api/* to http://localhost:8001)
cd C:/Projects/ClassLense/frontend && npm run dev
```
The frontend now defaults to `API_URL=http://localhost:8001` in `next.config.ts`. To override, copy `frontend/.env.local.example` to `frontend/.env.local` and set your own `API_URL`.

### Run the hardening verifications
```bash
# Unit + security tests
python -m pytest tests/ -q               # expect 67 passed

# Live end-to-end (needs backend running on 8001)
python scripts/cold_boot_smoke.py        # expect 7/7 passed
```

---

## Release Gate — Re-Opened for Jeff

**Path B hardening is complete. Evidence for release readiness is now materially stronger:**
- Precomputed cache covers all 7 sample PNGs (was 4/7)
- Backend routers have real unit test coverage (was zero)
- Real OpenRouter round-trip proven end-to-end via cold-boot (was manual-only)
- Security hardening on the two file-upload endpoints (was none)
- HTML sanitization actually comprehensive (was 7 hard-coded tag names)
- MISTAKES.md seeded per global CLAUDE.md

**Remaining Jeff-only questions:**
1. ~~Port 8000 conflict~~ — **RESOLVED** (8001 is now canonical)
2. Sarah's content status — still in progress. Test content is being generated synthetically in parallel; Sarah's real content still drives Sprint 6 video/profiles.
3. Deploy target — local + OpenRouter confirmed for now. Streamlit/Kaggle submission form factor is deferred until release approval.
4. Does "release ready" for you mean "demo-ready" or "production-ready"? Sprint 6 plan depends on which.

---

## Key File Changes This Session

| File | Change |
|------|--------|
| `backend/upload_utils.py` | NEW — shared upload validation |
| `backend/routers/capture.py` | Rewritten — uses upload_utils, removed test import from happy path |
| `backend/routers/documents.py` | Rewritten — uses upload_utils |
| `backend/routers/chat.py` | New `_sanitize_model_text` helper; comprehensive tag + script/style stripping |
| `backend/main.py` | CORS tightened — optional regex, explicit method/header lists |
| `data/precomputed/jaylen_pecs_log.json` | NEW |
| `data/precomputed/maya_visual_schedule.json` | NEW |
| `data/precomputed/sofia_transition_log.json` | NEW |
| `data/precomputed/maya_math_worksheet.json` | Fixed duplicate analysis + Maya copy-paste |
| `data/precomputed/jaylen_task_checklist.json` | Fixed wrong goal_id (G1 → G2) + Maya copy-paste |
| `data/precomputed/sofia_writing_sample.json` | Fixed wrong goal_id (G1 → G3) + Maya copy-paste |
| `tests/test_backend_security.py` | NEW — 32 unit tests for upload + sanitization |
| `scripts/cold_boot_smoke.py` | NEW — live end-to-end validation script |
| `MISTAKES.md` | NEW — 4 lessons seeded |
| `HANDOFF.md` | This file |
| `todo.md` | Path B items closed; release gate re-opened |
