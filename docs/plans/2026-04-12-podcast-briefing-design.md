# Progress Briefing Podcast — Design Document

**Date:** 2026-04-12
**Status:** Approved, awaiting implementation
**Branch target:** `nextjs-redesign` (or new feature branch)

## Overview

An AI-generated "mini podcast" that gives teachers a ~2-minute audio briefing on a student's progress. Gemma 4 (thinking mode) analyzes the student's full semester of IEP data and writes a two-speaker dialogue script. Edge TTS synthesizes the script to MP3 using distinct host/guest voices. Multilingual-capable.

## Competition Fit

- **Prize tracks strengthened:** Future of Education (primary), Digital Equity, Safety & Trust
- **Gemma 4 usage:** Thinking mode for data analysis + script writing. The "intelligence" is 100% Gemma; Edge TTS is commodity plumbing (like Plotly for charts)
- **Why Edge TTS (not Gemini TTS):** Keeps the narrative pure — Gemma does all reasoning; TTS is mechanical. No new API key, no cost, 300+ voices in 70+ languages
- **Demo value:** A 2-minute personalized audio briefing playing in the 3-minute demo video is viscerally compelling in a way screenshots cannot match

## Architecture

### Data flow

```
Student profile + trial data + alerts + trajectory data
        ↓
  Gemma 4 (thinking mode) → JSON dialogue script
        ↓
  Edge TTS (Host voice + Guest voice per line) → PCM/MP3 segments
        ↓
  Concatenate → MP3 saved to data/precomputed/podcast_{student_id}.mp3
        ↓
  Backend serves MP3 + script JSON to frontend
```

### Backend

**New agent:** `agents/podcast_producer.py`
- Follows the `BaseAgent` pattern
- Uses `generate_with_thinking()` — thinking trace exposed in UI
- Reuses long-context gathering logic from `trajectory_analyst.py`

**New module:** `core/tts_client.py`
- Thin wrapper around `edge-tts`
- Methods: `synthesize_line(text, voice) → bytes`, `concatenate_mp3(chunks) → bytes`
- Voice map:
  ```python
  VOICES = {
      "en": ("en-US-JennyNeural", "en-US-GuyNeural"),
      "es": ("es-MX-DaliaNeural", "es-MX-JorgeNeural"),
      "vi": ("vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"),
      "zh": ("zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"),
  }
  ```

**New router:** `backend/routers/podcast.py`
- `POST /api/students/{id}/podcast/stream` — SSE streaming with heartbeat messages ("Analyzing student data…", "Writing script…", "Synthesizing audio…", "Finalizing…")
- `GET /api/students/{id}/podcast` — returns cached script JSON + audio URL + `generated_date`, 404 if not generated
- `GET /api/podcast/audio/{student_id}.mp3` — serves MP3 with `Content-Type: audio/mpeg`. Validates `student_id` via `validate_student_id` (path traversal protection)

**Dependencies:** `edge-tts>=6.1.0` added to `requirements.txt`. No ffmpeg. No new API keys.

### Output schema

```json
{
  "student_id": "maya_2026",
  "title": "Maya's Progress Briefing — April 12",
  "script": [
    { "speaker": "host", "text": "Welcome back to your ClassLens briefing..." },
    { "speaker": "guest", "text": "Today we're looking at Maya's week..." }
  ],
  "language": "en",
  "generated_date": "2026-04-12",
  "audio_url": "/api/podcast/audio/maya_2026.mp3",
  "thinking": "(Gemma's reasoning chain)"
}
```

### Gemma 4 prompt design

**System prompt positions Gemma as a briefing writer:**
- Write a ~2-minute briefing (~300 words) as a Host/Guest dialogue
- Host introduces the student and sets context; Guest is the data analyst walking through each goal
- Be specific — cite actual percentages, trial counts, trend directions from the data
- Celebrate progress with concrete evidence; flag concerns with suggested next steps
- Use teacher-friendly language; no jargon; the listener may be driving to school
- For non-verbal students, emphasize AAC data and communication attempts as valid progress

**Output:** Strict JSON with script array; response parsed via `_parse_fallback` if thinking-mode text-wrap interferes with JSON extraction.

## Frontend

### Component placement

Below `TrajectoryReport` on `app/student/[id]/page.tsx`, between the Trajectory Report section and Materials Library section. New `<Separator />` divider.

### Component: `components/student/PodcastBriefing.tsx`

**Design language:** Matches existing components — `min-h-[44px]` touch targets, dashed-border trigger cards, SSE streaming with heartbeat messages, collapsible thinking trace, calm colors.

**Visual identity:** Headphones icon (`Headphones` from lucide-react). Section title: **"Progress Briefing"** (not "Podcast" — teacher-facing language).

**States:**

1. **Auto-loaded** (precomputed exists): Filled card (no dashed border).
   - Single row: Headphones icon, "Progress Briefing" label with timestamp badge, Play/Pause button, slim progress bar with MM:SS times, Download button (outline), Regenerate button (ghost).
   - Below row: collapsible "Show Script" toggle. Expanded view shows dialogue as alternating `bg-muted/50` / `bg-card` rows, speaker label prefix bolded ("Host:" / "Guest:"). No chat bubbles.

2. **Stale banner** (new data since generation): Amber banner above player:
   - "New data available since this briefing was generated."
   - **[Update Briefing]** button (amber accent, RefreshCw icon)
   - Triggers same SSE generation flow; overwrites old MP3.

3. **Empty** (no precomputed): Dashed-border card:
   - Headphones icon (muted, centered)
   - "Generate a 2-minute audio briefing on this student's progress."
   - "Generate Briefing" button with Headphones icon.

4. **Loading**: `border-primary/20 bg-primary/5`, spinner, pulsing SSE heartbeat message.

5. **Error**: `border-destructive/30 bg-destructive/5` with error message and Retry button.

### Update detection

On mount, compare podcast `generated_date` against student profile `last_updated`. If student updated more recently → show stale banner. Teacher decides when to update (no auto-regeneration — matches teacher-in-the-loop principle).

**What bumps `last_updated`:**
- New trial data (Vision/Voice Reader → IEP Mapper writeback)
- Profile edit (goals, interests, sensory profile)
- New alert triggered
- New material approved

### Regenerate confirmation

If teacher clicks Regenerate while audio is playing → pause audio first, then confirm: "This will replace the current briefing. Continue?"

### Download

- Filename: `{student_first_name}_briefing_{date}.mp3` (sanitized)
- Triggered via hidden `<a href={audio_url} download={filename}>` click

### Helpers

- `lib/formatTime.ts` — MM:SS formatter for progress bar

## Implementation Plan

### Phase 1 — Backend agent & endpoints (~half day)

1. `agents/podcast_producer.py` — new agent class; reuse context gathering from `trajectory_analyst.py`
2. `core/tts_client.py` — edge-tts wrapper with voice map
3. `backend/routers/podcast.py` — 3 endpoints (stream, get cached, serve MP3)
4. Register router in `backend/main.py`; update `requirements.txt`

### Phase 2 — Precomputed demo content (~30 min)

5. `scripts/generate_podcast_cache.py` — generates for Maya, Jaylen, Amara. Output committed to git.

### Phase 3 — Frontend component (~half day)

6. `components/student/PodcastBriefing.tsx` — all states
7. `lib/formatTime.ts` — MM:SS helper
8. Wire into student detail page between Trajectory Report and Materials Library

### Phase 4 — Tests (~half day)

9. `tests/test_podcast.py` — TestClient coverage:
   - 404 for nonexistent student
   - 404 when podcast not yet generated
   - Path traversal rejected on all 3 endpoints
   - MP3 served with correct Content-Type
   - Regenerate overwrites existing cache
10. Mock `edge-tts` in tests (no network in CI) — return ~1KB of silence bytes

### Phase 5 — Polish (~1 hour)

11. ASD accessibility audit:
    - `aria-label` on play/pause button
    - Transcript screen-reader accessible
    - Loading messages non-surprising
    - Download filename sanitized
12. Regenerate-while-playing confirmation dialog

## Total effort

**~1.5–2 days.** Zero new API keys. Zero architectural risk (additive only).

## Success criteria

- [ ] All 3 demo students have precomputed podcasts that play instantly on page load
- [ ] Playback works in Chrome, Safari, Firefox
- [ ] Update banner appears after a capture and triggers fresh generation
- [ ] Downloaded MP3 opens in any media player
- [ ] Multilingual synthesis verified for at least Spanish
- [ ] All tests green, zero TS errors, a11y audit passes

## Open questions for implementation

- Confirm Edge TTS output format works cross-browser without re-encoding (MP3 from edge-tts is broadly compatible; verify on Safari)
- Decide whether `generated_date` should be date or full timestamp for stale comparison precision
- Decide whether to expose voice choice to teacher (deferred — use fixed host/guest pair per language for MVP)

## Non-goals

- Live audio streaming (batch synthesis is fine; podcast is ~2 min MP3)
- Teacher voice cloning or custom voices (out of scope; Edge TTS voices are production-quality)
- Auto-regeneration on data changes (teacher-in-the-loop; stale banner only)
- Podcast history / versioning (latest wins; regenerate overwrites)
