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

**2026-04-12 acceleration sprint:** Three prize-track features shipped in one session:
- Feature 1: Long-context trajectory report — `trajectory_analyst.py` agent, `POST /api/students/{id}/trajectory` + stream, `TrajectoryReport.tsx` with per-goal status cards (On Track/At Risk/Stalled/Met), cross-goal patterns, IEP meeting talking points, thinking trace. Precomputed for Maya, Amara, Jaylen. 11 tests.
- Feature 4: Confidence panel — Material Forge now uses `generate_with_thinking()` for all outputs, `_compute_confidence()` scores based on data richness + hedge language in thinking trace. MaterialViewer shows confidence badges (High/Review Recommended/Flag for Expert), collapsible Gemma reasoning, Flag for Review button. `POST /api/materials/{id}/flag` endpoint stores flags in `data/flags/`. 9 tests. 24 existing materials migrated.
- Feature 3: Voice note capture — `voice_reader.py` agent with audio (Google AI Studio) and text fallback paths, `POST /api/capture/voice` + stream, `VoiceCapture.tsx` with MediaRecorder + base64 + preview + text fallback mode, `/capture/voice/supported` endpoint. Provider guard: non-google returns text_input fallback. 9 tests.
- Total: 99 pytest pass (excluding slow confidence suite), frontend builds clean 0 TS errors.

**2026-04-12:** All QA findings cleared, bilingual translate mode, unicode fix. 79/79 pytest, 7/7 live smoke, 24/24 post-capture. Zero deferred items.

**2026-04-11:** Full QA cycle — 12 findings all resolved, narrative guard 4/4, core/json_io.py, sample_inputs_smoke.py.
