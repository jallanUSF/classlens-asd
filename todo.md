# TODO — ClassLens ASD

## Active (5 items max)

1. [ ] **Release gate** — Jeff approval against `docs/RELEASE-READY.md` (56-item checklist) unblocks Sprint 6
2. [ ] Confirm Sarah's content status (profiles + video segments)
3. [ ] Verify `docs/PRIVACY-NOTICE.md` exists (SECURITY-REVIEW references it — may need to create)
4. [ ] Check `docs/VIDEO-SCRIPT.md` for any mic-dependent beats; rewrite as typed-observation flow if present
5. [ ] V2 roadmap: Gemma 4 E4B on-device ASR via LiteRT-LM (tracked in ADR-011 + decision doc)

## Sprint 6 — blocked on release gate

- [ ] Deploy target finalization
- [ ] 3-min video recording (against `docs/VIDEO-SCRIPT.md`)
- [ ] `docs/COMPETITION-WRITEUP.md` finalization
- [ ] Kaggle submission package
- [ ] Submit with 48h buffer before 2026-05-18

---

## Archive — shipped (chronological, most recent first)

**2026-04-12 audio decision:** Shipped Option C (text-first "Quick Observation"). Spike confirmed (1) AI Studio gates audio off on every Gemma variant served, (2) LiteRT-LM Python bindings are Linux/macOS only with Windows "upcoming" — four stacked unknowns for a marginal feature. Rewrote `docs/plans/2026-04-12-audio-shim-decision.md`, added ADR-011 with V2 Gemma 4 E4B on-device ASR roadmap. UI updated: `VoiceCapture.tsx` idle state now keyboard-icon + "Type Observation" primary (mic only renders when `audioSupported === true`); parent section title "Voice Observation" → "Quick Observation".

**2026-04-12 sprint items 1-3:** All 7 students now have real-Gemma podcast caches (added sofia/ethan/lily/marcus ~650-705KB each via `scripts/generate_podcast_cache.py`). Voice capture UX made honest — `_is_google_provider()` now gated on `VOICE_AUDIO_ENABLED` env var (defaults off because gemma-4-31b-it 400s on audio); audio validation moved before provider gate so MIME/size errors still return 400; `audio_not_supported` response path reached cleanly when gate closed. `VoiceCapture.tsx` shows "Type Observation" + explanatory copy when backend reports unsupported. Added `scripts/browser_smoke.py` (Playwright, closes MISTAKES.md #5 gap) — drives real frontend on :3000, verifies heading/trajectory/podcast/materials render + console clean across 3 students. 165/165 tests still passing, `next build` clean.

**2026-04-12 podcast briefing:** All 5 phases of `docs/plans/2026-04-12-podcast-briefing-design.md`. New podcast_producer agent (Gemma thinking mode), edge-tts wrapper, 3 backend endpoints, PodcastBriefing.tsx component, 10 tests, precomputed MP3s for Maya/Jaylen/Amara with real student-specific content. Flag dedup bug fixed (MISTAKES.md #7). Browser-verified. 154→165 tests.

**2026-04-12 quality hardening:** Security (validate_student_id on 4 routers, error sanitization), code quality (extracted duplicates to backend/sanitize.py, fixed 9 encoding violations, removed dead code), +29 TestClient tests, UX polish (precomputed data fix, a11y, prompt accuracy, ASD corrections). 128→137 tests.

**2026-04-12 acceleration sprint:** 3 prize-track features: trajectory report (256K context, 11 tests), confidence panel (thinking mode, 9 tests), voice capture (text fallback, 9 tests). 99→108 tests.

**2026-04-12:** QA findings cleared, bilingual translate, unicode fix. 79 tests, 7/7 smoke, 24/24 post-capture.

**2026-04-11:** Full QA cycle — 12 findings resolved, narrative guard, core/json_io.py.
