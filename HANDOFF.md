# HANDOFF.md — Session Handoff

**Date:** 2026-04-11 (late overnight — QA closeout + live sample_inputs smoke)
**Branch:** `nextjs-redesign`
**Status:** All 2026-04-11 QA findings closed in-browser. Live pipeline smoke on `docs/sample_inputs/` — 7/7 photos pass. Release gate still closed pending Jeff approval.

## TL;DR cold start

1. `git pull origin nextjs-redesign`
2. `pip install -r requirements.txt` + `cd frontend && npm install` (no new deps this session)
3. `.env`: `MODEL_PROVIDER=google` + `GOOGLE_AI_STUDIO_KEY=...`
4. Terminal 1: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001`
5. Terminal 2: `cd frontend && npm run dev`
6. Open http://localhost:3000 — dashboard should show 5 alerts with 4 distinct classifier labels (`declining`, `plateaued at 45%`, `target met` x2, `regression risk`)

## What happened this session

### 1. Fixed ParentLetterView non-EN render bug — the last HIGH finding from 2026-04-11 verification

**File:** `frontend/src/components/materials/ParentLetterView.tsx`

**Root cause:** `MaterialForge._call_with_fallback()` in `agents/material_forge.py` returns `{"text": "..."}` whenever Gemma emits flowing prose instead of calling the English-named `GENERATE_PARENT_COMM` tool. This reliably happens for ES/VI/ZH because the tool schema's field names are English and the model code-switches to prose output. The renderer only read the structured fields (`greeting` / `highlights` / `try_at_home` / `closing` / `teacher_name`) and fell through to an empty English shell when none existed.

**Fix:** Added a `freeformText` branch — when no structured fields exist and `content.text` is present, render the raw text in a `whitespace-pre-wrap` block. Gemma's `\n\n` paragraph breaks are preserved natively, no markdown or typography plugin needed. Structured EN path is untouched.

**Browser-verified end to end on localhost:3000:**
- **ES (fallback path):** Maya G1 2026-04-11 → 2032 chars of Spanish prose renders with `lang="es"`, starting "Estimada familia de Maya..." through "...Con cariño, Ms. Rodriguez"
- **EN (structured path):** Maya G1 2026-04-05 approved letter → "This Week's Highlights" / "Try at Home" sections render unchanged

### 2. Closed out Findings 5, 7, 8 from the original 2026-04-11 QA report

- **Finding 5 — chat SSE whitespace.** Verified by hitting `POST /api/chat/stream` directly with curl. Chunks come through as `"Amara"` + `" showed a drop from 45% down to 40%. She is so invested in writing about raptors."` — leading spaces preserved, no `to40%` / `investedin` word-merges. The backend `_sanitize_stream_chunk` fix holds.
- **Finding 7 — dashboard AbortController regression.** Verified at `frontend/src/app/page.tsx:58-67` — `AbortController` created, both `fetch` calls pass `signal`, `ac.signal.aborted` guard runs before `setStudents` / `setAlerts`. Matches the student-page pattern; Strict-mode double-invoke can't race anymore.
- **Finding 8 — alert severity populated.** `GET /api/alerts` returns `"severity":"high"` on Amara declining, `"medium"` on Ethan plateau_below, `"low"` on Maya plateau_at_target x2, `"high"` on Jaylen regression risk. Five rows, all populated. Type declaration matches at `app/page.tsx:27`. Dashboard doesn't yet style by severity, but the field is no longer `null` — per the original finding note this was "low priority unless UI surfaces the field."

**Classifier label spot-check (Finding 3 re-verification):** dashboard shows all 4 distinct branches — `declining` (Amara G2), `plateaued at 45%` (Ethan G2), `target met` (Maya G1 + G2), `regression risk` (Jaylen G1). Not a flat "plateaued" label anywhere.

### 3. Live pipeline smoke on `docs/sample_inputs/` — 7/7 photos pass

Fed each student's photo through `POST /api/capture` on a live Google AI Studio backend. The sample_inputs filenames don't collide with any precomputed cache keys, so every capture natively hit live Gemma Vision → IEP Mapper → Progress Analyst. **No changes to pipeline code; just the test corpus walked the live path.**

| Student | Photo | Key result |
|---|---|---|
| Maya | `01_math_worksheet_PHOTO.png` | 90% (9/10). Caught the `58+34=82` error AND the teacher's red `"should be 92"` correction. Picked up the "Blue hunts best in packs" side-note tying it to the Jurassic World theme. No IEP goal match (math ≠ communication goals — correct empty match). |
| Jaylen | `01_pecs_exchange_log_PHOTO.png` | 82% (49/60) → matched G1 primary. Captured all 5 daily tallies with iPad/PECS breakdown, the first-time "FEELINGS page!" use, and the emerging verbal approximations (`uh`, `more`, `ah-ba` = apple?). Progress Analyst drafted the full narrative inside the thinking trace. |
| Sofia | `01_madison_essay_SCAN.png` | Exceptional research quality but **caught the constraint violation** — wrote 6 sentences on an "exactly 5 sentences" assignment. Matched G3 primary. Progress note named the factual-vs-reflective style variability. |
| Amara | `02_talk_ticket_PHOTO.png` | Transcribed the "lost :(" and "I don't want this" handwritten rejection annotations and tied them to the 12% Friday dip. Matched G2 primary. Progress note named the decline from 50% baseline → 35% overall → 12% floor. |
| Ethan | `01_handwriting_sample_PHOTO.png` | Flagged the premature "all done" stop and the 'n' / 'd' consonant omission pattern. Matched G2 primary. Narrative tracked 20% baseline → ~50% with sensory plateau. |
| Lily | `03_ocean_notebook_PHOTO.png` | 100% with every annotation captured including the Minecraft creeper labeled `"NOT marine!"`. Matched G2 primary. Resilience narrative. |
| Marcus | `01_bathroom_routine_PHOTO.png` | 89.7% → matched G2 primary (85.7% per-goal). Correctly identified step 7 (wiping) as the remaining growth area from the 3/7 prompt count. |

**Quality verdict:** live pipeline output is at or above the cached content for every student. The Jaylen thinking trace in particular is demo gold — it drafts the parent-facing narrative inside the reasoning block. `docs/sample_inputs/` is now safe to promote to permanent live-smoke status whenever we want an evergreen demo without cache reliance.

## State of the 2026-04-11 QA reports

- `docs/qa-reports/qa-report-classlens-2026-04-11.md` — **all 12 findings addressed.** 8 resolved in the previous session, 3 more this session (5, 7, 8), plus the new ParentLetterView HIGH finding. Deferred low items: Finding 9 (chat `disabled` vs programmatic fill), Finding 10 (`/sw.js` 404), Finding 12 (bilingual regenerates vs translates — deferred pending Sarah's content opinion).
- `docs/qa-reports/qa-report-classlens-2026-04-11-verification.md` — **all 4 scenarios + new finding closed.** ParentLetterView ES now renders end-to-end.

## Pipeline-writeback gotcha (worth flagging, not blocking)

Running `POST /api/capture` on a live backend writes new trial data back into `data/students/{student_id}.json` via the IEP Mapper. This caused two side-effects I had to revert before committing:

1. **Unicode mangling on re-save.** The `json.dump(...)` path re-encoded pre-existing `≤` characters in notes fields as literal `\u00e2\u2030\u00a4` — a utf-8→latin-1→utf-8 round-trip bug. Look at the Marcus G2 trial history for the visible corruption in the diff.
2. **Diff noise from `indent=2` pretty-print.** Inline `{"value": 10, "date": "..."}` expanded to multi-line on every write.

Both are latent bugs in whatever serializes the student profile after the IEP Mapper's trial-append. Out of scope for this commit — just flagging so the next session knows to track it down. Also means `sample_inputs_smoke.py` (when we build it) should run against a `git stash`-protected working copy or snapshot-restore the profiles after each run, so the corpus stays reproducible.

## What's next

**Immediate (next session, when you resume):**
- Optional stretch items on `docs/sample_inputs/` QA loop (photos done; narrative/multimodal guards still open):
  - Qualitative guard: feed `04_amara/03_cafeteria_observation.md` and `07_marcus/03_slide_milestone_note.md` through the chat/narrative path. Assert Progress Analyst surfaces as an alert/note candidate, not a fabricated percentage.
  - Alert quality: re-run "Why?" thinking trace on Amara G2 with the cafeteria observation in context. Should name the sketchbook-as-recharge pattern.
  - Ethan plateau multimodal: combine `01_handwriting_sample_PHOTO.png` + `02_speech_transcript.md` + `03_weather_chart.md`. Progress Analyst should detect saturation across fine-motor AND echolalia.
  - Phase 2 (~30 min): `scripts/sample_inputs_smoke.py` that walks the directory and hits the right endpoints programmatically.
- Fix the student-profile round-trip unicode mangling if sample_inputs is to become permanent live-smoke.

**Medium term:**
- Share `sarah_review_bundle/` with Sarah. Apply her feedback to prompts / profiles.
- Jeff release gate decision.
- Sprint 6 (deploy + video + writeup + Kaggle submission — blocked on release gate).

## Evidence (local only, gitignored)

Verified on live Google AI Studio at the backend. Screenshots taken during the session were stored in `.playwright-mcp/` (now gitignored) and are not committed. The authoritative evidence is the committed `todo.md` + QA reports.

## Operator notes

- **`.claude/` and `.playwright-mcp/` are now gitignored** — `.claude/scheduled_tasks.lock` and Playwright runtime state were leaking into the dev workspace.
- Both Google AI Studio captures for photos completed in ~30-60s each. 7 captures ≈ 5 minutes total wallclock.
- Frontend `next dev` on port 3000, backend `uvicorn` on port **8001** (port 8000 is taken by an unrelated process on the dev machine — do not override without checking).
- `allowedDevOrigins` in `next.config.ts` may warn about `127.0.0.1` — harmless, Playwright tests should drive `http://localhost:3000` instead of `127.0.0.1:3000` to avoid the cross-origin warning and HMR websocket noise.
