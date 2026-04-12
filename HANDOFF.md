# HANDOFF.md — Session Handoff

**Date:** 2026-04-12
**Branch:** `nextjs-redesign`
**Commit:** `e9a5343`
**Status:** Quality hardening complete. 128 pytest pass (137 w/ slow suite), 0 TS errors. All features shipped. Release gate closed pending Jeff.

## Current state

Sprints 1–5 + acceleration sprint + quality hardening all done. The app is feature-complete for the hackathon demo.

### What's built
- **4-agent pipeline:** Vision Reader → IEP Mapper → Progress Analyst → Material Forge
- **3 prize-track features:** Trajectory Report (256K context), Voice Capture (text fallback), Confidence Panel (thinking mode)
- **7 material types:** lesson plan, parent letter, admin report, social story, tracking sheet, visual schedule, first-then board
- **20 work artifacts** with precomputed results — demo never waits on API
- **Full CRUD** for students, materials, alerts, documents, chat

### Test health
- 128 pytest pass (137 w/ slow confidence suite)
- 29 TestClient router tests covering students/chat/alerts/documents
- 0 TypeScript errors on `next build`

### Security posture
- All routers validate `student_id` (path traversal protection)
- All error responses sanitized (no `str(e)` leaks)
- Upload validation: extension allowlist, size limit, filename sanitization
- HTML sanitization on model output via `backend/sanitize.py`

## Open decisions (Jeff)

1. **Audio model** — Gemma 4 31B doesn't support audio input (only E4B/E2B, not on Google AI Studio API). Options: (A) Gemini for transcription step, (B) two-step Gemini→Gemma, (C) keep text fallback. Tabled for now.
2. **Release gate** — blocks all downstream work
3. **Sarah's content** — profiles, video segments, sample voice notes

## TL;DR cold start

```bash
git pull origin nextjs-redesign
pip install -r requirements.txt && cd frontend && npm install
# .env: MODEL_PROVIDER=google, GOOGLE_AI_STUDIO_KEY=...
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001  # terminal 1
cd frontend && npm run dev                                         # terminal 2
# Open http://localhost:3000
```

## Operator notes

- Backend on port **8001** (8000 is taken on dev machine)
- Audio returns 400 on `gemma-4-31b-it` — text fallback always works
- Flags stored in `data/flags/` (not `data/students/`)
- Slow confidence tests: `--ignore=tests/test_confidence.py` for fast iteration
- Shared utilities in `backend/sanitize.py` (sanitize_model_text, has_real_model_credentials)
