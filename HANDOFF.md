# HANDOFF.md — Session Handoff

**Date:** 2026-04-12
**Branch:** `nextjs-redesign`
**Commit:** `0a79078` (see `git log` for full trail — 6 new commits this session)
**Status:** Podcast Briefing feature shipped end-to-end + flag dedup bug fixed. 165 pytest pass, 0 TS errors. Browser-verified with real Gemma output.

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
