# HANDOFF.md — Session Handoff

**Date:** 2026-04-11
**Branch:** `nextjs-redesign`
**Status:** Path B hardening + live browser QA fixes complete. Release gate re-open for Jeff.

---

## TL;DR for a cold start

1. Clone, `pip install -r requirements.txt`, `cd frontend && npm install`.
2. Copy `.env.example` → `.env`, set `MODEL_PROVIDER=openrouter` + `OPENROUTER_API_KEY=...`.
3. Terminal 1: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001` — **8001 is canonical**, don't use 8000 (ulana.main squats it on the dev machine).
4. Terminal 2: `cd frontend && npm run dev` — frontend auto-proxies `/api/*` to 8001.
5. Open http://localhost:3000 — dashboard, 7 students, real Gemma via OpenRouter, all 11 sample PNGs cache-hit the pipeline.
6. Tests: `python -m pytest tests/ -q` (71 green) and `python scripts/cold_boot_smoke.py` (8/8 green against a live backend).

Everything below is context for *why* things are the way they are.

---

## What happened this session (2026-04-11)

Three phases in one sitting:

### Phase 1 — Path B hardening (commits `d46c898`, `d700d7c`)
Project Manager + QA Manager sub-agents reviewed Sprints 1–5 and flagged that "35/35 tests pass" was all-mock — zero coverage on the FastAPI routers, the `load_dotenv` fix, image upload, or the real OpenRouter API path. Chose Path B (one hardening week) before Sprint 6.

- **Precomputed cache gap closed** — 3 new artifacts + 3 mis-mapped existing ones fixed (Maya copy-paste bugs, wrong goal_ids).
- **Security pass** — new `backend/upload_utils.py`: filename sanitize, path-traversal blocks on student IDs, 10 MB cap, extension allowlist. Capture + documents routers rewritten to use it. CORS tightened (opt-in regex, explicit method/header lists). Production→test coupling (`MockGemmaClient` import) removed from the happy path.
- **HTML sanitization** — `_sanitize_model_text` now drops `<script>`/`<style>` blocks with bodies and strips any tag with attributes. Old regex only caught 7 hard-coded tag names.
- **Port 8001 canonicalized** — frontend `next.config.ts` default, CLAUDE.md tech stack rewritten for Next.js + FastAPI reality, HANDOFF + todo updated.
- **Synthetic test content** — sub-agent generated 4 new work artifacts (Maya + Jaylen), 4 matching precomputed JSONs, 2 mock IEP PDFs, extended `scripts/generate_sample_work.py` + new `scripts/generate_sample_ieps.py`.
- **Test coverage** — `tests/test_backend_security.py` added 32 unit tests (upload validation + sanitization). Total 67/67.
- **Live cold-boot smoke** — `scripts/cold_boot_smoke.py` runs real HTTP against a fresh uvicorn: health, students, **real OpenRouter chat round-trip**, capture happy path (new cache entry), 3 validation rejections. 8/8 green.
- **MISTAKES.md seeded** — 4 lessons from Sprints 1–5 per global CLAUDE.md mandate.

### Phase 2 — Live browser QA (Chrome DevTools MCP)
Started real backend + frontend, drove Chrome through the actual UI. Logged everything the user would do: dashboard load → student page → real chat (Gemma via OpenRouter returned Maya-specific response referencing "Blue the raptor" and correctly identifying the 75% G2 plateau) → upload `maya_reading_comprehension.png` → full pipeline result rendered as a chat action card → navigate to Jaylen → upload `jaylen_turn_taking_tally.png` → Gordon/Percy transcription + G3 match. Zero console errors, zero failed network requests. Screenshots in `data/documents/qa_screenshots/` (gitignored).

Surfaced 3 bugs, two real fixes and one product decision.

### Phase 3 — Bug fixes (commit `<hash>` — this session's commit)

1. **G3 count-based goal display** — Maya's G3 "reduce outbursts to 1 or fewer per day" was rendering as `Target: 1%` which is meaningless. Backend now annotates goals with `target_unit`, `target_value`, `target_display`. Count-based goals (`target ≤ 10` + description contains one of "fewer/reduce/outburst/incident/per day") render as `≤1/day` with the progress bar normalized to 100. Percentage goals unchanged. New unit tests in `test_backend_security.py::TestAnnotateGoalTarget`.

2. **React Strict Mode double-fetch** — every `useEffect` data-loader was firing twice in dev. Added `AbortController` to 5 call sites: `app/page.tsx`, `app/student/[id]/page.tsx`, `components/sidebar/StudentSidebar.tsx`, `components/student/RecentWork.tsx`, `components/student/MaterialsLibrary.tsx`. Verified in browser: first fetch now shows `ERR_ABORTED`, only the second reaches the backend. Half the network traffic in dev, correct production behavior guaranteed.

3. **Chat history not scoped to student** — switching from Maya to Jaylen kept Maya's conversation in the chat panel. `ChatProvider.setActiveStudent` now tracks the previous ID in a `useRef` and calls `clearHistory()` outside the setState updater before setting the new ID. Using the ref (instead of an updater callback) avoids Strict Mode double-invoking the side effect. Verified in browser: Maya's chat cleanly resets to welcome + "Now looking at Jaylen" when switching.

Also caught along the way:
- Latent bug in student page's context message: used stale `alerts.length` state instead of the just-loaded value, always showing "How can I help?" instead of the real alert count. Now uses local `studentAlerts` — verified rendering "2 alert(s) need attention" for Maya, "1 alert(s)" for Jaylen.
- `data/documents/` added to `.gitignore` (runtime upload state + QA screenshots — should never be committed).

---

## Current state

### What works end-to-end
- Dashboard loads with 7 students, 5 alerts, sessions counter
- Student navigation, chat (real OpenRouter Gemma 3 27B), work image upload → pipeline → structured chat action card
- 11 sample PNGs all precomputed — demo never waits on live API for capture
- 2 mock IEP PDFs for `/api/documents/upload` testing
- All 3 browser QA bugs fixed, zero console errors, zero failed network requests
- Backend + frontend boot cleanly on 8001/3000

### Test state (all green)
- `python -m pytest tests/ -q` — **71/71 pass** (was 35 at session start, added 32 security + 4 goal-annotation)
- `cd frontend && npx next build` — **0 errors** with Next 16.2.2 + Turbopack
- `python scripts/cold_boot_smoke.py` — **8/8 live checks** against real backend + real OpenRouter
- Browser QA (Chrome DevTools MCP) — **0 console errors, 0 failed requests** across the full user path on both Maya and Jaylen

### What's still open
- **Sarah's content** — still Sarah's job, in progress. Synthetic test content covers development/QA; Sarah's real content drives Sprint 6 video + profile validation.
- **Deploy target decision** — local + OpenRouter for testing; Streamlit/Kaggle submission form factor deferred until release gate opens. CLAUDE.md has been updated to reflect the Next.js + FastAPI active stack and the Streamlit dormant stack.
- **"Release ready" definition** — still needs Jeff's explicit criterion (demo-ready vs. production-ready).

---

## Release gate — still re-open for Jeff

**Path B hardening + browser QA both complete. Evidence for release readiness:**

Strong:
- Real unit tests on real code paths (71/71)
- Live cold-boot smoke proves real API round-trip (not just manual)
- Browser QA with Chrome DevTools walked through the golden path successfully
- All 3 browser-QA findings fixed and re-verified
- Security hardening on both upload endpoints + CORS
- Precomputed cache covers every sample artifact (no live-API fallthrough during demo)
- MISTAKES.md + CLAUDE.md aligned with reality
- Port 8001 baked in everywhere that matters

Remaining Jeff-only decisions:
1. Sarah's real student profiles/video segments ready?
2. What specific evidence would move you from "awaiting approval" to "approved"?
3. Once approved, Sprint 6 scope: deploy → video → writeup → Kaggle notebook → submit with buffer before 2026-05-18.

---

## Key file changes this session

| File | What changed |
|------|-------------|
| `backend/upload_utils.py` | NEW — shared upload validation (phase 1) |
| `backend/routers/capture.py` | Rewritten with upload_utils; removed test import from happy path |
| `backend/routers/documents.py` | Rewritten with upload_utils |
| `backend/routers/chat.py` | `_sanitize_model_text` helper; comprehensive HTML stripping |
| `backend/routers/students.py` | `_annotate_goal_target` helper; adds target_display/target_unit/target_value to each goal |
| `backend/main.py` | CORS tightened |
| `frontend/next.config.ts` | Default `API_URL` → `http://localhost:8001` |
| `frontend/.env.local.example` | NEW — documents the override |
| `frontend/src/app/page.tsx` | AbortController for dashboard fetches |
| `frontend/src/app/student/[id]/page.tsx` | AbortController; uses local studentAlerts for context msg |
| `frontend/src/components/sidebar/StudentSidebar.tsx` | AbortController |
| `frontend/src/components/student/RecentWork.tsx` | AbortController |
| `frontend/src/components/student/MaterialsLibrary.tsx` | AbortController |
| `frontend/src/components/student/GoalCard.tsx` | Renders `target_display` when present |
| `frontend/src/context/ChatContext.tsx` | Uses `useRef` to track previous student; clears chat on student switch |
| `data/precomputed/*.json` | 4 new, 3 Maya copy-paste bugs fixed |
| `data/sample_work/*.png` | 4 new synthetic artifacts |
| `data/sample_iep/*.pdf` | 2 new mock IEP PDFs |
| `scripts/generate_sample_work.py` | Extended with 4 new worksheet layouts |
| `scripts/generate_sample_ieps.py` | NEW — reportlab-based IEP PDF generator |
| `scripts/cold_boot_smoke.py` | NEW + expanded to 8/8 checks |
| `tests/test_backend_security.py` | NEW + 32+4 unit tests |
| `MISTAKES.md` | NEW — 4 seeded lessons |
| `CLAUDE.md` | Tech stack rewritten for Next.js + FastAPI reality |
| `HANDOFF.md` | This file |
| `todo.md` | Path B closed |
| `.gitignore` | Added `data/documents/` |

---

## Agent files for next session

`~/.claude/agents/project-manager.md` and `~/.claude/agents/qa-manager.md` are in place. They weren't hot-loaded this session (new agent files register on next restart), so this session used `general-purpose` with inlined personas. Next session they'll be directly invokable via `subagent_type: "project-manager"` and `subagent_type: "qa-manager"`.

---

## Commits on `nextjs-redesign` this session

```
<latest>  Fix G3 target display, AbortController, scope chat to student
d700d7c   Canonicalize port 8001 + expand synthetic test content
d46c898   Path B hardening: security, coverage, cache completion
783d355   Sprint 5 finalization: real Gemma API + image upload pipeline
```

All pushed to origin.
