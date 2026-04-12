# TODO — ClassLens ASD

## Active — next session (5 items, forward-looking)

1. [ ] **Sample inputs — narrative/qualitative guard.** Feed `docs/sample_inputs/04_amara/03_cafeteria_observation.md` and `07_marcus/03_slide_milestone_note.md` through the chat/narrative path. Progress Analyst must surface these as alert/note candidates, not fabricate trial percentages from narrative text. Catches hallucinated data.
2. [ ] **Sample inputs — Ethan plateau multimodal.** Combine `05_ethan/01_handwriting_sample_PHOTO.png` + `02_speech_transcript.md` + `03_weather_chart.md`. Progress Analyst should detect saturation across fine-motor AND echolalia.
3. [ ] **Sample inputs — Alert quality re-run.** "Why?" thinking trace on Amara G2 with the cafeteria observation in context. Should name the sketchbook-as-recharge pattern.
4. [ ] **Share `sarah_review_bundle/` with Sarah** and apply her feedback to prompts / student profiles.
5. [ ] **Release gate.** Jeff approval for release readiness (blocks Sprint 6 deploy + video + Kaggle submission).

## Deferred / low priority

- [ ] **Finding 9** — Chat send button `disabled` state doesn't react to programmatic `fill`. Harmless for humans; blocks Playwright/chrome-devtools automation.
- [ ] **Finding 10** — `/sw.js` 404 on every page load. Ship a minimal `public/sw.js` stub or remove the manifest reference.
- [ ] **Finding 12** — Bilingual letters regenerate independently instead of translating the approved EN version. Consider after Sarah has opinions on demo bilingual quality.
- [ ] **Student-profile round-trip unicode mangling.** The IEP Mapper's write-back path corrupts existing unicode (e.g. `≤` → `\u00e2\u2030\u00a4`) and reformats inline objects. See `HANDOFF.md` "Pipeline-writeback gotcha" for scope. Blocks `sample_inputs_smoke.py` being snapshot-safe.
- [ ] **Phase 2 sample_inputs smoke (~30 min):** `scripts/sample_inputs_smoke.py` that walks the directory and hits the right endpoints programmatically. Blocked on the unicode round-trip fix above if we want it reproducible.

## Jeff open questions (before Sprint 6)

- [ ] Confirm Sarah's content status (profiles + video segments)
- [ ] Define "release ready" criterion (demo-ready vs production-ready)

## Sprint 6 — blocked on release gate

- [ ] Deploy target finalization
- [ ] 3-min video recording (against `docs/VIDEO-SCRIPT.md`)
- [ ] `docs/COMPETITION-WRITEUP.md` finalization
- [ ] Kaggle submission package (eventual Streamlit form factor transition)
- [ ] Submit with 48h buffer before 2026-05-18

---

## Archive — shipped (chronological, most recent first)

**2026-04-11 late:** ParentLetterView non-EN render bug fixed (ES/VI/ZH now render via `content.text` whitespace-pre-wrap fallback). Findings 5 (chat SSE whitespace), 7 (dashboard AbortController guard), 8 (alert severity populated) all re-verified live. `docs/sample_inputs/` photo path 7/7 pass on live Google AI Studio — Vision Reader → IEP Mapper → Progress Analyst with production-quality output for every student.

**2026-04-11 overnight:** Closed 8 of 12 findings from `qa-report-classlens-2026-04-11.md` — Findings 1 (stream every Gemma endpoint via `_sse.run_streaming_job` with heartbeats), 2 (deterministic alert ids via sha256 of `{student}_{goal}_{label}`), 3 (alert label classifier — `declining` / `plateau_below` / `plateau_at_target`), 4 (`FirstThenView.tsx` renderer), 5 (`_sanitize_stream_chunk` without `.strip()`), 6 (IEP extraction dedupe by normalized description prefix), 7 (dashboard AbortController guard), 8 (severity populated), 11 (Spanish teacher-name threading). Live browser verification pass — 3 of 4 scenarios PASS, new HIGH finding (ParentLetterView, fixed above).

**2026-04-11 day:** 5 judge-appeal features shipped — IEP PDF auto-extraction (pymupdf + Gemma multimodal), chat SSE streaming, thinking-trace "Why?" UI, first_then enum wiring, bilingual parent comms (EN/ES/VI/ZH). Flipped to Google AI Studio as the canonical provider.

**Sprint 5 finalization:** Real API wiring, image upload pipeline, 9 new synthetic work artifacts (Amara x2, Ethan x2, Lily x2, Marcus x2, Sofia x1), 2 alert scenarios (Amara G2 regression, Ethan G2 plateau), Windows font fallback in `generate_sample_work.py`.

**Path B hardening:** Missing precomputed JSONs filled, Maya copy-paste bugs fixed, security pass (filename sanitization, student_id validation, upload size/extension limits), CORS hardening (regex allowlist, explicit methods/headers), HTML sanitization rewrite, 32 security unit tests, `cold_boot_smoke.py`, `MISTAKES.md` seeded, port 8001 canonical, synthetic test content (4 new work PNGs + 2 mock IEP PDFs).

**Sprints 2-5:** Next.js + Tailwind + shadcn/ui scaffold, 3-column layout, student sidebar, class dashboard, student detail page with expandable goals + Plotly charts + alerts, chat panel SSE streaming, recent work timeline, materials library, quick actions, Add Student conversational flow, 6 professional material renderers (+ MaterialViewer sheet), print CSS, approve/regenerate controls, mobile responsive (hamburger + FAB), OpenRouter + deployment config, design review polish passes.
