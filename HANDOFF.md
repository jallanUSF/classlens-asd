# HANDOFF.md — Session Handoff

**Date:** 2026-04-12 (end of long session)
**Branch:** `nextjs-redesign` (clean tree; pushed)
**HEAD:** `23f405f`
**Status:** 165/165 pytest, `next build` clean, 0 TS errors. 5 commits this session on top of `60cfbb6`.

## Commits landed this session (oldest → newest)

| SHA | Summary |
|---|---|
| `d40cb7c` | Text-first observation capture + sprint risks 1-3 (podcast caches, voice UX, browser smoke) |
| `7536e94` | UI polish pass: 5 fixes for judge-facing demo + COMPETITION-WRITEUP restructure |
| `1eaa4ee` | Ignore Playwright MCP audit artifacts |
| `02e1bef` | Drop PRIVACY-NOTICE.md requirement; add V2 audio roadmap |
| `23f405f` | Audit VIDEO-SCRIPT.md against shipped app |

## What's shipped (judge-facing)

**Features:** 4-agent pipeline + Trajectory Report + Confidence Panel + Quick Observation (text) + Progress Briefing Podcast. 7 students with **real-Gemma precomputed caches** for all demo paths — zero live-API waits.

**Code health:** 165 tests green. `next build` clean. Desktop layout no longer content-starves the main column (chat collapsed by default, opens via right-side Sheet). Gemma 4 branding visible in sidebar on every page. Level badges shape-coded for colorblind access. Landing page has one-sentence product banner.

**Docs that matter for submission:**
- `docs/COMPETITION-WRITEUP.md` — rewritten from 923 lines to 184. Opens with Sarah's Friday afternoon; 5-7 hrs/week anchor; ADR-011 foregrounded as maturity signal.
- `docs/ADR.md` — 11 ADRs, most recent (ADR-011) documents text-first V1 + Gemma 4 E4B on-device V2.
- `docs/RELEASE-READY.md` — 55-item binary checklist (dropped one item when PRIVACY-NOTICE was removed).
- `docs/plans/2026-04-12-audio-shim-decision.md` — spike findings + decision.
- `docs/plans/2026-04-12-audio-v2-roadmap.md` — V2 plan with three concrete trigger conditions.
- `docs/plans/2026-04-12-ui-polish-design.md` — the five UI fixes shipped in `7536e94`.
- `docs/VIDEO-SCRIPT.md` — accuracy-audited against shipped app (7 button/port fixes).

## todo.md open items

1. **Release gate** — Jeff's call. Review `docs/RELEASE-READY.md` end-to-end against the built app and approve.
2. **Sarah's content** — human dependency (profiles + video segments).
3. **Optional**: add video beats for Quick Observation, Progress Briefing Podcast, and Trajectory Report — these are shipped features the current video script doesn't demo. Not blocking; consider if you want to lean on them as additional Gemma 4 differentiators.

## Cold-start for next session

```bash
git pull origin nextjs-redesign
cd C:\Projects\ClassLense
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001   # terminal 1
cd frontend && npm run dev                                          # terminal 2
# Open http://localhost:3000 — lands on dashboard; click any student.
# Chat panel now collapsed by default on desktop; toggle via bubble icon top-right.
```

Tests: `python -m pytest tests/ -q` (165 tests, ~5-6 min on CPU)
Browser smoke: `python scripts/browser_smoke.py` (after `pip install playwright && playwright install chromium`)

## What NOT to revisit

- **Audio model decision** — closed via ADR-011. Don't reopen without new information (Windows LiteRT-LM binding release is the only trigger).
- **Writeup structure** — restructure is shipped in `7536e94`. Tweak prose, don't rebuild shape.
- **Podcast caches** — all 7 students cached from real Gemma. Only regen if content policy changes.

---

## Audio decision (2026-04-12) — shipped Option C

**Spike findings that killed the other options:**
1. AI Studio gates audio off on every Gemma variant — confirmed via live 400s: `gemma-4-31b-it` ("Audio Part rejected"), `gemma-3n-e4b-it` and `gemma-3n-e2b-it` both return `"Audio input modality is not enabled"`.
2. Google AI Edge Eloquent uses Gemma 4 E4B via LiteRT-LM — but the Python bindings are **Linux/macOS only**, Windows listed as "upcoming". `pip install litert-lm-api-nightly` on this Windows Server box → no matching distribution. Local WSL is WSL1, not WSL2.

**Decision:** Ship text-first ("Quick Observation"). 100% Gemma 4 on every intelligent call, zero new infra, zero demo-day risk. V2 adds on-device Gemma 4 E4B ASR when LiteRT-LM ships Windows support (tracked in ADR-011).

**UI changes (text-first observation capture):**
- `frontend/src/components/student/VoiceCapture.tsx` — idle state now keyboard-icon + "Type a quick observation. One or two sentences is plenty." with "Type Observation" primary button. Record button only renders when backend reports `audioSupported === true` (V2 gate). Done-state label "Voice observation captured" → "Observation captured".
- `frontend/src/app/student/[id]/page.tsx` — section title "Voice Observation" → "Quick Observation".
- MediaRecorder code kept dormant; V2 re-enables with a single `VOICE_AUDIO_ENABLED=1` flip.

**Docs updated:**
- `docs/plans/2026-04-12-audio-shim-decision.md` — rewritten with spike findings + final decision + V2 roadmap
- `docs/ADR.md` — added ADR-011 (text-first V1 / Gemma 4 E4B on-device V2)

---

## Later session (2026-04-12) — risks 2 & 3 addressed

**Voice capture UX made honest.** Gemma 4 31B returns 400 on audio input, but `/api/capture/voice/supported` was advertising it as available. Fixed:
- `backend/routers/capture.py`: `_is_google_provider()` now also requires `VOICE_AUDIO_ENABLED=1`; default off until an audio path is wired. Audio shape validation (MIME, 10MB limit) moved before the provider gate so malformed submissions still 400 cleanly. Text-only shortcut (text_fallback without audio_b64) routes straight to `transcribe_from_text`.
- `frontend/src/components/student/VoiceCapture.tsx`: when `audioSupported === false`, copy reads "Audio input isn't available right now. Type your observation below." and the "Type Observation" button becomes primary. Record button hidden. No more mid-submit failures for judges who try the mic.
- `tests/test_voice_capture.py`: one test broadened to recognize `audio_not_supported` as a legitimate graceful outcome. All 165 tests still pass.

**Browser-path smoke test added** — `scripts/browser_smoke.py` (Playwright). Closes the gap flagged in MISTAKES.md #5 (TestClient can't catch Next.js proxy / SSR / hydration regressions). Drives real frontend on :3000, checks page load, heading render, Trajectory / Progress Briefing / Materials sections, console clean. Runs across 3 core students by default. Exits non-zero on any fail. Run before every demo-critical change.

    # preconditions: backend :8001, frontend :3000, playwright installed
    pip install playwright && playwright install chromium
    python scripts/browser_smoke.py           # all 3 students
    python scripts/browser_smoke.py maya_2026 # single
    python scripts/browser_smoke.py --headed  # visible browser

**Risk 1 closed:** All 7 students now have real-Gemma podcast caches. Added sofia (635KB), ethan (678KB), lily (652KB), marcus (705KB). Generated via `scripts/generate_podcast_cache.py <id>` against Google AI Studio. Minor cosmetic issue: Marcus's script says "Grade 0" instead of "Kindergarten" — regenerate if Sarah flags it.

---

## Earlier session (2026-04-12 afternoon)

## This session (2026-04-12 afternoon)

Built the **Progress Briefing Podcast** feature from the approved design doc at `docs/plans/2026-04-12-podcast-briefing-design.md`. All 5 phases shipped.

### New files
- `agents/podcast_producer.py` — Gemma thinking-mode agent writing Host/Guest dialogue scripts
- `core/tts_client.py` — Edge TTS wrapper, 4-language voice map (en/es/vi/zh)
- `backend/routers/podcast.py` — 3 endpoints (stream generate, get cached, serve MP3)
- `frontend/src/components/student/PodcastBriefing.tsx` — player + stale banner + script collapsible
- `frontend/src/lib/formatTime.ts` — MM:SS formatter
- `scripts/generate_podcast_cache.py` — regenerates cache for Maya/Jaylen/Amara
- `tests/test_podcast.py` — 10 tests, mocked TTS so CI never hits network
- `data/precomputed/podcast_{maya,jaylen,amara}_2026.{json,mp3}` — real Gemma content, ~600KB MP3s

### Bug fixes
- **Flag dedup** in `backend/routers/materials.py` — blind-append replaced with update-or-append by `material_id`. Cleaned 3 stale dupes in `data/flags/maya_2026.json`.
- **MP3 inline serve** — removed `Content-Disposition: attachment` from FileResponse (was forcing download instead of inline `<audio>` playback).
- **Gitignore** — added `.next/` (Next.js build artifact) and committed `data/flags/` (was untracked).

### Verified live
- Backend serves MP3 with `audio/mpeg`, no attachment header
- Path traversal blocked (`..maya.mp3` → 400)
- Next.js renders the Progress Briefing section between Trajectory and Materials
- Play button flips to Pause, script expands to 12 Host/Guest lines
- Real Maya-specific content: "Blue the raptor" interest, 20%→80% peer greetings, 6/8 two-step directions, noise-canceling headphones, fidget cube
- Zero console errors, zero TS errors, 165/165 pytest

## Current state

Sprints 1–5 + acceleration sprint + quality hardening + podcast briefing all done. Release gate still closed pending Jeff.

### What's built
- **4-agent pipeline:** Vision Reader → IEP Mapper → Progress Analyst → Material Forge
- **4 prize-track features:** Trajectory Report, Voice Capture (text fallback), Confidence Panel, **Progress Briefing Podcast (new)**
- **7 material types:** lesson plan, parent letter, admin report, social story, tracking sheet, visual schedule, first-then board
- **20 work artifacts** with precomputed results — demo never waits on API

### Test health
- **165 pytest pass** (was 154, +10 podcast tests + 1 flag dedup test)
- 0 TypeScript errors on `next build`
- Live browser check passed (Playwright)

### Security posture
- All routers validate `student_id` (path traversal protection) — podcast router included
- Flag endpoint now dedups by `material_id` instead of blind-appending
- Upload validation unchanged: extension allowlist, size limit, filename sanitization

## Open decisions (Jeff)

1. **Audio model** — Gemma 4 31B doesn't support audio input. Options: (A) Gemini for transcription, (B) two-step Gemini→Gemma, (C) keep text fallback. Tabled.
2. **Release gate** — blocks deploy/video/submission.
3. **Sarah's content** — profiles, video segments, sample voice notes.

## TL;DR cold start

```bash
git pull origin nextjs-redesign
pip install -r requirements.txt && cd frontend && npm install
# .env: MODEL_PROVIDER=google, GOOGLE_AI_STUDIO_KEY=...
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001  # terminal 1
cd frontend && npm run dev                                         # terminal 2
# Open http://localhost:3000/student/maya_2026 to see the podcast
```

## Operator notes

- Backend on port **8001** (8000 is taken on dev machine)
- Podcast regeneration: `python scripts/generate_podcast_cache.py [student_id]` (omit for all 3). Use `--mock` for offline.
- Edge TTS needs network; tests mock `core.tts_client.synthesize_script`.
- Audio returns 400 on `gemma-4-31b-it` — voice capture text fallback always works.
- Flags stored in `data/flags/` (not `data/students/`). Endpoint dedups by `material_id`.
- Shared utilities in `backend/sanitize.py` (`sanitize_model_text`, `has_real_model_credentials`).
