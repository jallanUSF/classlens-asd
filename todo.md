# TODO — ClassLens ASD

## Active (5 items max)

1. [ ] **Audio model decision** — Gemma 4 31B doesn't support audio (only E4B/E2B, not on AI Studio). Options: (A) Gemini for transcription step, (B) two-step Gemini→Gemma, (C) keep text fallback. Jeff to decide.
2. [ ] **Release gate** — Jeff approval (blocks Sprint 6 deploy + video + Kaggle submission)
3. [ ] Confirm Sarah's content status (profiles + video segments)
4. [ ] Record sample voice notes for demo (Sarah or synthetic)
5. [ ] Define "release ready" criterion (demo-ready vs production-ready)

## Sprint 6 — blocked on release gate

- [ ] Deploy target finalization
- [ ] 3-min video recording (against `docs/VIDEO-SCRIPT.md`)
- [ ] `docs/COMPETITION-WRITEUP.md` finalization
- [ ] Kaggle submission package
- [ ] Submit with 48h buffer before 2026-05-18

---

## Archive — shipped (chronological, most recent first)

**2026-04-12 podcast briefing:** All 5 phases of `docs/plans/2026-04-12-podcast-briefing-design.md`. New podcast_producer agent (Gemma thinking mode), edge-tts wrapper, 3 backend endpoints, PodcastBriefing.tsx component, 10 tests, precomputed MP3s for Maya/Jaylen/Amara with real student-specific content. Flag dedup bug fixed (MISTAKES.md #7). Browser-verified. 154→165 tests.

**2026-04-12 quality hardening:** Security (validate_student_id on 4 routers, error sanitization), code quality (extracted duplicates to backend/sanitize.py, fixed 9 encoding violations, removed dead code), +29 TestClient tests, UX polish (precomputed data fix, a11y, prompt accuracy, ASD corrections). 128→137 tests.

**2026-04-12 acceleration sprint:** 3 prize-track features: trajectory report (256K context, 11 tests), confidence panel (thinking mode, 9 tests), voice capture (text fallback, 9 tests). 99→108 tests.

**2026-04-12:** QA findings cleared, bilingual translate, unicode fix. 79 tests, 7/7 smoke, 24/24 post-capture.

**2026-04-11:** Full QA cycle — 12 findings resolved, narrative guard, core/json_io.py.
