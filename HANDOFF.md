# HANDOFF.md — Session Handoff

**Date:** 2026-04-06
**Branch:** `nextjs-redesign`
**Status:** Sprints 1-5 COMPLETE + real API & image upload wired. Awaiting Jeff's release approval.

---

## What Was Done (This Session)

### 1. Wired Real Gemma API to Chat
- **Root cause:** `load_dotenv()` wasn't called in backend routers, so `.env` vars were invisible at request time
- **Fix:** Added `load_dotenv()` to `backend/routers/chat.py` and `backend/routers/capture.py`
- **Config:** Added `MODEL_PROVIDER=openrouter` and `OPENROUTER_MODEL=google/gemma-3-27b-it` to `.env`
- **Verified:** Chat returns personalized, context-aware responses using Maya's real IEP data
- **Bonus:** Added HTML tag sanitization to strip stray `<td>` etc. from model output

### 2. Wired Image Upload to Capture Pipeline
- **QuickActions "Scan Work"** — Now opens a native file picker instead of prefilling chat text. Uploads to `POST /api/capture` with `student_id` via FormData
- **Chat paperclip button** — Added attachment button to ChatPanel input area. Enabled when a student is selected, disabled with tooltip otherwise
- **Pipeline results in chat** — Upload results (transcription, matched goals, accuracy, alerts) render as a structured chat message with "Work Captured" action card
- **Precomputed fallback** — Pipeline now strips date/type prefixes from uploaded filenames to match precomputed cache (e.g., `2026-04-06_worksheet_maya_math_worksheet` → `maya_math_worksheet`)
- **Files changed:** `useChat.ts` (uploadWork), `ChatContext.tsx` (expose uploadWork), `QuickActions.tsx` (file input), `ChatPanel.tsx` (paperclip button), `pipeline.py` (cache fallback)

### 3. QA Pass
- Dashboard: 7 students, 21 goals, 123 sessions, 5 alerts — all rendering correctly
- Chat: Real Gemma API responses via OpenRouter, personalized to student context
- Image upload: Capture endpoint returns precomputed results with transcription + goal mapping
- Build: 0 TypeScript errors
- Tests: 35/35 Python tests passing

---

## Current State

### What Works
- Full end-to-end: Dashboard → Student → Chat (real API) → Scan Work (file upload → pipeline → results in chat)
- All 10 design audit findings addressed
- Precomputed demo data for all sample work images
- Mobile responsive layout
- 3 material renderers with print CSS

### Known Limitations
- Port 8000 may be occupied by ulana.main — use `API_URL=http://localhost:8001` or kill the process
- Model occasionally emits stray HTML (now stripped server-side)
- No SSE streaming (responses arrive as single JSON — fine for demo)

---

## How to Resume

### Start the app
```bash
# Terminal 1: Backend (use port 8001 if 8000 is occupied)
cd C:/Projects/ClassLense && uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd C:/Projects/ClassLense/frontend && npm run dev

# Open: http://localhost:3000
```

### Run tests
```bash
cd C:/Projects/ClassLense && python -m pytest tests/ -v
cd C:/Projects/ClassLense/frontend && npx next build
```

---

## Next Steps

Sprint 6 (deploy, demo recording, video production, Kaggle submission) is **NOT on the todo list** and will NOT be added until Jeff explicitly approves release readiness.

---

## Key File Changes This Session

| File | Change |
|------|--------|
| `backend/routers/chat.py` | Added `load_dotenv()`, HTML sanitization |
| `backend/routers/capture.py` | Added `load_dotenv()`, `os` import |
| `core/pipeline.py` | Precomputed cache fallback for prefixed filenames |
| `frontend/src/hooks/useChat.ts` | Added `uploadWork()` function |
| `frontend/src/context/ChatContext.tsx` | Exposed `uploadWork` in context |
| `frontend/src/components/student/QuickActions.tsx` | File picker for Scan Work, added `studentId` prop |
| `frontend/src/components/chat/ChatPanel.tsx` | Paperclip attachment button |
| `frontend/src/app/student/[id]/page.tsx` | Pass `studentId` to QuickActions |
| `.env` | Added `MODEL_PROVIDER=openrouter`, `OPENROUTER_MODEL` |
