# RELEASE-READY.md — ClassLens ASD

Binary pass/fail checklist gating the release: deploy, 3-minute video recording, and Kaggle submission. Every item ticks or it doesn't. No item ships on "mostly."

Target submission deadline: **2026-05-18** (with 48h buffer).

---

## 1. Functional

- [ ] Backend boots clean on `127.0.0.1:8001` via `python -m uvicorn backend.main:app`
- [ ] Frontend boots clean on `localhost:3000` via `npm run dev` and proxies `/api/*` to 8001
- [ ] All 7 student profiles load in the sidebar (maya, jaylen, sofia, amara, ethan, lily, marcus)
- [ ] Each of the 7 students opens a detail page without error
- [ ] Vision Reader path produces structured JSON for at least one artifact per student (20 artifacts total)
- [ ] IEP Mapper path returns goal mappings with confidence scores for every student
- [ ] Progress Analyst renders trend summary + alert banner for both `amara_social_tracker` and `ethan_handwriting_probe`
- [ ] Material Forge generates all 7 material types (lesson plan, parent letter, admin report, social story, tracking sheet, visual schedule, first-then board)
- [ ] Trajectory Report endpoint `/api/students/{id}/trajectory` returns goal-level status for all 7 students
- [ ] Voice Capture: text-fallback path submits cleanly; when `VOICE_AUDIO_ENABLED=0` the UI shows "Type Observation" and hides Record
- [ ] Confidence Panel renders `high` / `review_recommended` / `flag_for_expert` on material outputs
- [ ] Flag endpoint `POST /api/materials/{id}/flag` dedups by `material_id` (no blind append)
- [ ] Progress Briefing Podcast plays inline (no forced download) for all 7 students

## 2. Demo integrity

- [ ] `data/precomputed/` holds a 1:1 cached result for every artifact in `data/sample_work/`
- [ ] `data/precomputed/trajectory_{student_id}.json` exists for all 7 students
- [ ] `data/precomputed/podcast_{student_id}.json` + `.mp3` exist for all 7 students
- [ ] No demo path makes a live Gemma call (verified by running with `GOOGLE_AI_STUDIO_KEY` unset)
- [ ] Marcus podcast "Grade 0" vs "Kindergarten" decision made and applied
- [ ] No `TODO`, `FIXME`, `Lorem ipsum`, or placeholder copy visible in any rendered UI surface
- [ ] `python scripts/cold_boot_smoke.py` exits 0 against a freshly booted backend
- [ ] `python scripts/test_pipeline.py` exits 0 offline (no backend, no network)

## 3. Stability

- [ ] `python -m pytest tests/ -q` — all tests green (currently 165/165)
- [ ] `python -m pytest tests/test_backend_security.py -v` — green
- [ ] `cd frontend && npx next build` — 0 TypeScript errors, 0 build warnings treated as errors
- [ ] `python scripts/browser_smoke.py` — exits 0 across all 3 core students
- [ ] `python scripts/browser_smoke.py` — console clean (no red errors) across Trajectory, Progress Briefing, Materials sections
- [ ] No open entries in MISTAKES.md marked "unresolved"

## 4. Security / Privacy

- [ ] `.env` present in `.gitignore`; `.env.example` has placeholder only
- [ ] `git log -p --all -S "GOOGLE_AI_STUDIO_KEY"` shows no leaked key
- [ ] `git log -p --all -S "OPENROUTER_API_KEY"` shows no leaked key
- [ ] All 4+ routers call `validate_student_id` (path-traversal guard) on any student-id path param
- [ ] Upload validation enforces MIME allowlist + 10MB cap + filename sanitization
- [ ] Podcast MP3 route rejects `..` traversal (verified: `..maya.mp3` returns 400)
- [ ] Error responses route through `backend/sanitize.py` — no raw model text, no stack traces
- [ ] All student JSON reads/writes route through `core/json_io.py` (UTF-8, `ensure_ascii=False`)
- [ ] `docs/SECURITY-REVIEW.md` Section 5 "Before Launch" checklist fully ticked
- [ ] `PRIVACY-NOTICE.md` exists at repo root and states synthetic-data-only

## 5. Content (Sarah)

- [ ] All 7 student profiles in `data/students/` reviewed and approved by Sarah
- [ ] All 20 artifacts in `data/sample_work/` reviewed and approved by Sarah
- [ ] Sarah's opening 30-second classroom monologue (Shot 1 of VIDEO-SCRIPT) recorded
- [ ] Sarah's closing segment recorded per VIDEO-SCRIPT
- [ ] All B-roll clips Sarah is responsible for delivered (no student faces)
- [ ] Sample voice observations in `data/sample_voice/` recorded (or synthetic accepted)

## 6. Submission artifacts

- [ ] 3-minute video recorded against `docs/VIDEO-SCRIPT.md` shot list (all cumulative timestamps hit)
- [ ] Video shows at least one close-up of function-calling JSON (per VIDEO-SCRIPT "Technical Depth Moments")
- [ ] Video shows thinking-mode reasoning trace visible on-screen
- [ ] Video exported at 1080p, under Kaggle file-size limit, audio levels consistent
- [ ] Video uploaded to public host (YouTube unlisted or equivalent) and link verified
- [ ] `docs/COMPETITION-WRITEUP.md` finalized — no TODOs, numbers verified, authors named
- [ ] Live public URL deployed and reachable from a fresh incognito browser
- [ ] Live URL opens dashboard in under 5 seconds cold
- [ ] GitHub repo public, `README.md` links to video + live URL + writeup
- [ ] Kaggle submission package assembled (notebook or link-out per competition rules)
- [ ] Submission uploaded with ≥48 hours before 2026-05-18 deadline
