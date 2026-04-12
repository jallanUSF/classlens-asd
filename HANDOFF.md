# HANDOFF.md — Session Handoff

**Date:** 2026-04-11 (late-night — unicode fix + Findings 9/10 + sample_inputs smoke)
**Branch:** `nextjs-redesign`
**Status:** All four actionable deferred items closed in one session. `core/json_io.py` centralizes UTF-8 JSON read/write for every student-profile site; 4 profiles normalized to canonical format; Findings 9 + 10 shipped; `scripts/sample_inputs_smoke.py` built and verified 7/7 PASS on live Google AI Studio with byte-perfect snapshot/restore. 79/79 pytest pass. Release gate still closed pending Jeff approval.

## TL;DR cold start

1. `git pull origin nextjs-redesign`
2. `pip install -r requirements.txt` + `cd frontend && npm install` (no new deps this session)
3. `.env`: `MODEL_PROVIDER=google` + `GOOGLE_AI_STUDIO_KEY=...`
4. Terminal 1: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001`
5. Terminal 2: `cd frontend && npm run dev`
6. Open http://localhost:3000 — dashboard should show 5 alerts with 4 distinct classifier labels (`declining`, `plateaued at 45%`, `target met` x2, `regression risk`)
7. Optional live smoke: `python scripts/sample_inputs_smoke.py` (~17 min against Google AI Studio, snapshot/restores student profiles)

## What happened this session (late-night, after narrative guard)

### 1. Fixed the Windows unicode round-trip bug (the HANDOFF's "Pipeline-writeback gotcha")

**Root cause (empirically confirmed).** Python's default `open(path)` uses the system locale encoding, which is **cp1252** on this Windows dev box. Reading `marcus_2026.json`'s literal `≤` (UTF-8 bytes `E2 89 A4`) decoded those bytes as three cp1252 chars `â‰¤`; writing back via `json.dump(..., indent=2)` with the default `ensure_ascii=True` then escaped each as `\u00e2\u2030\u00a4` — the exact visible corruption in the original writeback diff. Reproduced in a 10-line Python script against the real marcus profile before touching any code.

**Fix.** New module `core/json_io.py` with two functions (`read_json` / `write_json`) that enforce `encoding="utf-8"`, `ensure_ascii=False`, `indent=2`, and `default=str`. Migrated every student-profile read/write site to the helper:
- `agents/base.py` — `_load_student_raw` / `_save_student_raw` (the site IEP Mapper calls)
- `core/state_store.py` — `load_student` / `save_student` / `export_student_data`
- `core/pipeline.py` — `_load_profile`
- `backend/routers/students.py` — `_read_profile` / `_write_profile` + list loop
- `backend/routers/chat.py` — `_load_student_context` + mock path
- `backend/routers/alerts.py` — `get_alerts` + `_find_current_alert` student loops
- `tests/conftest.py` — state_store fixture

**Normalization.** Shipped `scripts/normalize_student_profiles.py` (idempotent, `--dry-run` supported) and ran it once. The 4 newer profiles (`amara`, `ethan`, `lily`, `marcus`) had inline `{"value": N, "date": "..."}` baseline objects that `json.dump(indent=2)` always expands. Normalization brings them into canonical format so writebacks diff to zero. Post-normalization marcus still stores `≤` as literal UTF-8 bytes (no escapes, no mojibake).

**Regression coverage.** `tests/test_json_io.py` — 8 tests locking the contract:
- Unicode round-trip preserves `≤`, `≥`, `→`, accented chars, emoji, mixed strings
- Multiple read→write cycles remain idempotent (no mojibake buildup)
- Output contains literal UTF-8 bytes, not `\uXXXX` escape sequences
- `indent=2` two-space indentation locked
- cp1252 bytes raise `UnicodeDecodeError` loudly instead of silently mojibaking
- Real `marcus_2026.json` round-trips without mojibake
- `BaseAgent._load_student_raw` + `_save_student_raw` on unchanged data is **byte-idempotent**
- BaseAgent writeback on mutated data preserves pre-existing `≤` characters

**Out-of-scope but noted in `todo.md`:** the same bug shape exists in `materials.py`, `documents.py`, `capture.py`, `core/pipeline.py` (precomputed cache), and `alerts.py` (alerts cache). Not blocking the demo because those caches don't round-trip through the IEP Mapper. Same one-line fix shape whenever we touch them.

### 2. Sample inputs live smoke — 7/7 PASS on live Google AI Studio

**New script:** `scripts/sample_inputs_smoke.py`. Walks every PHOTO/SCAN in `docs/sample_inputs/` through `POST /api/capture` on the live backend. Snapshots all 7 student profiles as raw bytes before starting and restores them on exit (including SIGINT / SIGTERM), then asserts the restore is byte-identical. This pattern is only reproducible because the unicode round-trip bug is now fixed — previously, every live capture would have left corrupted files behind.

**Live run results:**

| # | Student | Photo | Elapsed | Matched | Verdict |
|---|---|---|---|---|---|
| 1 | maya_2026 | 01_math_worksheet_PHOTO.png | 80.5s | — (correct: math ≠ communication goals) | PASS |
| 2 | jaylen_2026 | 01_pecs_exchange_log_PHOTO.png | 150.0s | G1 | PASS |
| 3 | sofia_2026 | 01_madison_essay_SCAN.png | 128.8s | G3 | PASS |
| 4 | amara_2026 | 02_talk_ticket_PHOTO.png | 173.2s | G2 | PASS |
| 5 | ethan_2026 | 01_handwriting_sample_PHOTO.png | 157.6s | G2 | PASS |
| 6 | lily_2026 | 03_ocean_notebook_PHOTO.png | 123.0s | G2 | PASS |
| 7 | marcus_2026 | 01_bathroom_routine_PHOTO.png | 217.1s | G2 | PASS |

Total wall-clock: ~17 minutes against Google AI Studio. Report: `docs/qa-reports/sample_inputs_smoke_2026-04-11.md`. Post-run `git diff data/students/` shows only the 4 normalization changes from step 1 — snapshot restore was byte-perfect across 7 live IEP Mapper writebacks.

### 3. Finding 9 — Chat send button disabled race (Playwright automation unblock)

**File:** `frontend/src/components/chat/ChatPanel.tsx`. **Root cause:** Playwright's programmatic `.fill()` sets the DOM `value` directly, bypassing React's synthetic event system, so controlled `input` state stays empty and `disabled={!input.trim() || isStreaming}` keeps the button disabled. **Fix:** drop `!input.trim()` from the disabled prop — `handleSubmit` already guards empty submits with `if (!input.trim() || isStreaming) return`, so the only behavioral difference is that the button is now always clickable while idle and no-ops on empty (same UX for humans, unblocks automation).

### 4. Finding 10 — `/sw.js` 404 on every page load

**Fix:** added `frontend/public/sw.js` as a minimal no-op service worker (`install`/`activate` listeners, nothing else). Stops the 404 noise. No `layout.tsx` or manifest reference exists, so nothing registers the worker — it just serves 200 when the browser auto-probes.

### 5. Bonus — verified `core/json_io` migration doesn't break anything

Full pytest suite: **79/79 pass** (was 77/77 before the 2 new BaseAgent idempotency tests). No router, agent, or pipeline path regressed.

## Previous session summary (narrative guard — still current)

### 0. Sample inputs narrative guard — 4/4 pass on live Google AI Studio

**New script:** `scripts/sample_inputs_narrative_guard.py`. Walks four scenarios through `POST /api/chat` with each student's profile loaded into the system prompt via `_load_student_context`, then checks the response for fabricated percentages and expected clinical vocabulary.

**Percentage fabrication detector.** First cut fired a false positive: Gemma emitted Amara's real `45% → 42% → 40%` G2 trial history when asked "what do you see?" — that's recall from the profile injected into the system prompt, not invention. Second cut builds an allowlist by pulling every pct token from the student's actual profile AND every pct token that appears verbatim in the observation prose, and only flags pct tokens that live outside both sets. `_load_profile_pct_tokens()` + `_tokens_in_source()` in the script. Also had to hard-force UTF-8 on stdout because Gemma's Marcus milestone response contained `🌟` and Windows cp1252 crashed the encoder.

**Results:**

| # | Scenario | Elapsed | Verdict | Notes |
|---|---|---|---|---|
| S1a | Amara cafeteria observation (narrative guard) | 34.9s | PASS | 6/6 keywords. Naturally names withdrawal, masking, social capacity, sketchbook-as-regulation, food refusal as stress signal. No fabricated numbers. |
| S1b | Marcus slide milestone (narrative guard) | 29.3s | PASS | 4/5 keywords. Renders as celebration narrative tagged for the student file — no numeric trial recording. Offers a G1 AAC motivator tie-in (`"I want slide"` on TouchChat). |
| S2 | Amara G2 Why? with cafeteria context | 29.5s | PASS | 5/5 keywords — **explicitly names "recharge mode" + sketchbook + My Hero Academia** as the regulation pattern. Frames decline as capacity-vs-skill, not regression. Drafts IEP team talking points. |
| S3 | Ethan plateau multimodal saturation | 43.8s | PASS | 6/7 keywords. **Reframes "saturation" as "regulation mismatch / sensory bottleneck"** — notes G1 is *progressing* (Echo→Functional bridge) while G2 plateau is postural/core fatigue, not letter-formation skill. Proposes vertical-surface probe + high-interest topic swap. Stronger than the test expected. One `100%` pct match is figurative ("I'm 100% behind the weighted vest") — detector is regex-simple, verdict passed on keywords. |

**Report:** `docs/qa-reports/sample_inputs_narrative_guard_2026-04-11.md` (166 lines, full responses captured).

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

## Pipeline-writeback gotcha — RESOLVED in the late-night session above

Original symptoms (unicode mangling + inline-object diff noise) both fixed via `core/json_io.py` migration, one-shot `scripts/normalize_student_profiles.py`, and verified idempotent under a 17-minute live capture cycle by `scripts/sample_inputs_smoke.py`. See "What happened this session (late-night, after narrative guard)" above.

## What's next

**Immediate (next session, when you resume):**
- Finding 12 — bilingual re-translate vs regenerate (pending Sarah's opinion).
- Optional: migrate the remaining non-student JSON caches (materials/documents/capture/precomputed/alerts) to `core.json_io` — same bug shape, not blocking.

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
