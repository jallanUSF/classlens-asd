# Audio V2 Roadmap — On-Device Gemma 4 ASR for Voice Observations

**Date:** 2026-04-12
**Owner:** Jeff
**Status:** Roadmap — deferred until trigger conditions met
**Predecessor:** `docs/plans/2026-04-12-audio-shim-decision.md` (V1 shipped text-first)
**Related ADR:** ADR-011 (voice input architecture)

---

## 1. Objective

Deliver on-device Gemma 4 automatic speech recognition for teacher voice observations so ClassLens preserves a 100% Gemma-family narrative on every intelligent call, runs offline on a classroom device, and meets the privacy bar that FERPA-sensitive districts require when student names and behavior notes are spoken aloud. The target runtime is Google AI Edge's LiteRT-LM executing `litert-community/gemma-4-E4B-it-litert-lm` (or the Gemma 3n E4B interim if Gemma 4 E-series audio does not surface through the Python binding), invoked from the existing FastAPI backend with zero network dependency for the audio path. Text-first remains the V1 default; the V2 audio path turns on automatically when the backend reports `supported=true` through `GET /api/capture/voice/supported`.

---

## 2. Trigger Conditions

Do not start Phase 1 until **all three** conditions are true. Each is independently verifiable — check before kicking off.

### 2.1 LiteRT-LM Python bindings ship with Windows support

- **Check:** `pip install litert-lm` (or `pip install litert-lm-api-nightly`) on Windows Server 2022 succeeds and `python -c "import litert_lm; print(litert_lm.__version__)"` runs.
- **Reference point:** As of 2026-04-12 the Google AI Edge docs say *"Python API of LiteRT-LM for Linux and macOS (Windows support is upcoming)"* and the nightly wheel returns `No matching distribution found` on Windows. The trigger is met when that language is removed from the docs and a Windows wheel appears on PyPI or Google's index.
- **How to recheck later:** Re-run the install command above; re-read https://ai.google.dev/edge/litert/lm docs section on Python support.

### 2.2 Gemma 4 E-series audio confirmed through the LiteRT-LM Python API

- **Check:** The official LiteRT-LM Python example for audio input references a `gemma-4-E*` model (not just Gemma 3n), OR a direct spike loads `litert-community/gemma-4-E4B-it-litert-lm` and accepts an audio part without error.
- **Reference point:** As of 2026-04-12 the audio example in LiteRT-LM docs cites Gemma 3n E4B/E2B. Gemma 4 E4B audio via Python binding is ambiguous.
- **Fallback if only Gemma 3n E4B audio works through the Python binding:** Acceptable — still pure-Gemma family. Document in ADR-011 addendum as "V2 shipped on Gemma 3n E4B for audio, Gemma 4 31B for reasoning."

### 2.3 V1 shipped and submitted to Kaggle

- **Check:** Kaggle submission confirmed, May 18 2026 deadline passed, the live URL is stable, and the hackathon judging window is open or closed.
- **Why this gate:** Do not fork attention away from V1 stability before submission. Any V2 exploration during the sprint window risks regressions on the text-first path that is the actual graded artifact.

---

## 3. Plan by Phase

### Phase 1 — Feasibility spike (1 day)

**Goal:** Prove the runtime loads, accepts audio, and returns a transcription fast enough to be useful, on the actual dev hardware (Windows Server 2022, CPU-only).

**Tasks:**
1. `pip install litert-lm` in a fresh venv on the Windows dev box. Capture install output.
2. Download `litert-community/gemma-4-E4B-it-litert-lm` (approx. 3.65 GB). If Gemma 4 E-series is not audio-capable through the binding, fall back to `litert-community/gemma-3n-E4B-it-litert-lm`.
3. Write a throwaway script `scripts/spike_litert_audio.py` that:
   - Loads the model cold.
   - Feeds a 10-second WAV clip from `data/sample_voice/` (same assets used by the V1 text-fallback harness).
   - Measures wall-clock latency for: cold load, warm transcription, schema parse.
   - Prints the raw transcript and confirms audio part acceptance (no HTTP 400 equivalent).

**Pass gates (all required):**
- Cold model load succeeds without NPU/GPU errors on a CPU-only machine.
- Warm transcription of a 10-second clip returns plausible English text in ≤3 seconds.
- Output can be routed into `VoiceReader._parse_result` without schema changes (same fields as `transcribe_and_extract` returns today: `transcription`, `work_type`, `subject`, `student_work`, `confidence`).

**Fail gates (any one → fall back per Section 4):**
- Install fails on Windows.
- Model load requires an NPU hint that a generic Windows CPU cannot satisfy.
- Transcription latency exceeds 10 seconds on a 10-second clip (unusable for a teacher in-the-moment).
- Audio part is rejected.

**Deliverable:** A one-page spike report appended to this doc under "Phase 1 Results" with the four pass-gate measurements or a clear fail diagnosis.

### Phase 2 — Backend integration (2-3 days)

**Goal:** Wire the LiteRT-LM runtime into the existing voice pipeline behind the same flag that already gates audio, with no regression to the 165 existing tests.

**Tasks:**

1. **New module `core/ondevice_asr.py`** — wraps LiteRT-LM.
   - Class `OnDeviceASR` with methods `load()` (lazy, memoized), `is_ready() -> bool`, and `transcribe(audio_bytes: bytes, mime_type: str) -> str`.
   - Handles mime-type normalization (webm → wav via ffmpeg if LiteRT-LM rejects webm directly; confirm in Phase 1).
   - Raises `OnDeviceASRUnavailable` when the runtime fails to initialize, so the router can gracefully degrade.

2. **Extend `agents/voice_reader.py`** — add `transcribe_ondevice(audio_bytes, mime_type, student_id)`.
   - Same signature shape as `transcribe_and_extract`.
   - Steps: (a) call `OnDeviceASR.transcribe` to get raw text; (b) reuse the existing `transcribe_from_text` prompting path to structure it against the student's IEP goals via `self.client.generate(...)`.
   - Output dict is schema-identical to the Vision Reader output, same as today.

3. **Update `backend/routers/capture.py`.**
   - Add a module-level `_ondevice_asr: Optional[OnDeviceASR]` initialized on first use.
   - Change `_is_google_provider()` (consider renaming to `_is_audio_supported()` in this pass) so it returns `True` when: `VOICE_AUDIO_ENABLED=1` AND either the current Gemma API supports audio OR the on-device ASR initialized successfully.
   - In `_run_voice_capture`, when audio bytes are present and on-device ASR is ready, route to `reader.transcribe_ondevice(...)` instead of `reader.transcribe_and_extract(...)`. Keep the existing API-audio path intact for if/when Google unblocks audio on AI Studio.
   - Preserve the precomputed cache check and the text-only shortcut unchanged.
   - `GET /api/capture/voice/supported` continues to report a single `supported` boolean — the UI does not need to know which audio backend is active.

4. **Tests (no regressions, add coverage).**
   - Mock `OnDeviceASR` the same way `MockGemmaClient` is mocked today (see `tests/mock_api_responses.py`). Add a `MockOnDeviceASR` returning a deterministic transcript for a fixed WAV fixture.
   - New test file `tests/test_voice_ondevice.py`:
     - `test_ondevice_asr_init_succeeds` — `is_ready()` True after `load()`.
     - `test_voice_reader_transcribe_ondevice_matches_schema` — output dict matches `tests/gold_standard_outputs.json` shape.
     - `test_capture_route_prefers_ondevice_when_ready` — with `VOICE_AUDIO_ENABLED=1` and `MockOnDeviceASR.is_ready()=True`, audio bytes route to `transcribe_ondevice`.
     - `test_capture_route_falls_back_to_text_when_asr_unavailable` — with `OnDeviceASRUnavailable` raised at load, response matches the existing `{"error": "audio_not_supported", "fallback": "text_input"}` shape.
   - Full `python -m pytest tests/ -q` must pass with 0% degradation (165 → 169 tests green).

5. **Configuration.**
   - Add `LITERT_MODEL_PATH` env var (default: `models/gemma-4-E4B-it-litert-lm`).
   - Add `LITERT_MAX_AUDIO_SECONDS` env var (default: 30) for safety.
   - Document both in `.env.example` and `CLAUDE.md` Tech Stack Context.

### Phase 3 — UI re-enable (half day)

**Goal:** The UI already degrades correctly; this phase is copy and verification.

**Tasks:**

1. **No structural change to `frontend/src/components/student/VoiceCapture.tsx`.** The component already conditionally renders the Record button when `audioSupported === true` (lines 259-268) and keeps the MediaRecorder path dormant-but-wired. Once the backend flips `supported=true`, the mic button appears automatically.

2. **Copy updates in `VoiceCapture.tsx`:**
   - Idle state helper text (line 248-250): add a second line when `audioSupported === true` — "Record a quick voice observation — transcribed on-device by Gemma 4."
   - Submitting state message for the audio path: "Transcribing on-device…" (replaces "Processing voice observation…" in `submitAudio`, line 101).
   - Done state label: "Voice observation captured" when the audio path produced the result, "Observation captured" when the text path did. Distinguish via a new `capture_method` field returned from the API.

3. **Copy update in `frontend/src/app/student/[id]/page.tsx`:** Section title can stay "Quick Observation" — no mandatory change. If the video script calls for "Voice Observation" framing, flip it back here.

4. **Verification:** Run the full-story verification checklist from the `verification` skill — UI renders, client → API round trip works, server logs show `OnDeviceASR.transcribe` was hit, response renders in the Done state, no console errors. Capture evidence in the Phase 3 results section of this doc.

---

## 4. Fallback Plan

If Phase 1 fails at decision-time — LiteRT-LM still lacks Windows bindings, or Gemma 4/3n E-series audio is not reachable through the Python API — exercise these in order:

1. **Vertex AI Gemma 3n E4B audio.** Paid but pure-Gemma. Requires a GCP project with billing and a Vertex endpoint for `gemma-3n-e4b-it`. Swap `core/ondevice_asr.py` for `core/vertex_asr.py` with identical surface, same router branch. Cost: roughly $0.0001/second of audio at current Vertex pricing — low enough that a teacher using the feature 20 times a day stays under $1/month.

2. **Keep text-first permanently. Close V2 as rejected.** Update ADR-011 with an addendum — "V2 audio closed: no pure-Gemma audio path materialized on our hardware within the budget window." The text-first path remains the product. Remove the "V2 roadmap" reference from the ADR so we stop advertising a promise we cannot keep.

Not chosen as fallback: a Gemini transcription shim. Same reasoning as the V1 decision — mixing Gemini into the critical audio path undermines the Gemma-family narrative that is the entire point of this feature.

---

## 5. Success Criteria

V2 ships when all five are demonstrable:

1. **Latency.** A 10-second voice observation returns a transcribed, IEP-structured result in ≤3 seconds on the Windows CPU-only dev machine, measured warm (after one prior invocation).
2. **Test parity.** `python -m pytest tests/ -q` shows 0% degradation vs. V1's 165 passing tests (new tests from Phase 2.4 add to, not replace, the existing suite).
3. **Offline.** End-to-end path — record in browser → capture.py → OnDeviceASR → IEP Mapper → response rendered — works with the Windows machine's network adapter disabled. Confirms no dependency on AI Studio or any other network service for the audio path.
4. **Narrative match.** UI copy references "on-device by Gemma 4" (or Gemma 3n, per Phase 1 outcome). Docs — `README.md`, `docs/ADR.md` (ADR-011), `docs/VIDEO-SCRIPT.md` if re-recorded — match.
5. **Teacher-in-the-loop preserved.** Transcript is editable before submission. No auto-send.

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LiteRT-LM Python bindings remain nightly-only past trigger date | Medium | High (blocks Phase 1) | Fallback Section 4.1 (Vertex Gemma 3n) |
| Gemma 4 E4B on-device requires NPU hints absent on generic Windows CPU | Medium | High (blocks Phase 1) | Try Gemma 3n E4B; failing that, Section 4.1 |
| Schema mismatch between on-device output and `VoiceReader._parse_result` | Low | Medium | Phase 1 pass-gate #3 explicitly tests this; fix with parser adapter in `core/ondevice_asr.py` |
| Model download size (3.65 GB) blocks deployment to low-storage classroom devices | Low | Medium | Document disk requirement in `docs/RELEASE-READY.md`; consider Gemma 3n E2B (~1.8 GB) for constrained hardware |
| webm-from-MediaRecorder is not accepted by LiteRT-LM | Medium | Low | Convert to wav via ffmpeg in `OnDeviceASR.transcribe`; add ffmpeg dep to `requirements.txt` only if needed |
| Cold-load latency (first request after server boot) exceeds teacher patience | Medium | Medium | Lazy-load on FastAPI `startup` event with a background task; expose `/api/capture/voice/supported` returning `warming` state |
| Competing audio demos in judging window that do use cloud Gemma audio make on-device narrative feel like a cop-out | Low | Low | Lead with the FERPA/offline story, not the technical novelty — "student audio never leaves the classroom device" is the punchline |

---

## 7. Effort Estimate

| Phase | Engineering days | Calendar (solo, focused) |
|---|---|---|
| Phase 1 — Feasibility spike | 1 | 1 day |
| Phase 2 — Backend integration | 2-3 | 3-4 days (buffer for test churn) |
| Phase 3 — UI re-enable + verification | 0.5 | 1 day |
| **Total** | **4-5 days** | **5-6 calendar days** |

Not included: waiting for the trigger conditions in Section 2. Those are external gates — Google ships Windows bindings on Google's timeline.

---

## 8. Artifacts

### Created

- `core/ondevice_asr.py` — LiteRT-LM wrapper
- `scripts/spike_litert_audio.py` — Phase 1 throwaway (delete after spike report archived)
- `tests/test_voice_ondevice.py` — Phase 2 test file
- `models/gemma-4-E4B-it-litert-lm/` (or gemma-3n-E4B) — downloaded weights, gitignored

### Modified

- `agents/voice_reader.py` — add `transcribe_ondevice()`
- `backend/routers/capture.py` — route audio to on-device path when ready; rename `_is_google_provider` → `_is_audio_supported`
- `frontend/src/components/student/VoiceCapture.tsx` — copy updates only (Section 3.2)
- `frontend/src/app/student/[id]/page.tsx` — optional title revert
- `tests/mock_api_responses.py` — add `MockOnDeviceASR`
- `tests/gold_standard_outputs.json` — add on-device transcription fixture if needed
- `.env.example` — `LITERT_MODEL_PATH`, `LITERT_MAX_AUDIO_SECONDS`
- `CLAUDE.md` — Tech Stack Context adds LiteRT-LM line; Commands section adds spike script
- `docs/ADR.md` — ADR-011 addendum with the V2 outcome (success, Gemma 3n fallback, or rejection)
- `docs/RELEASE-READY.md` — note disk requirement for on-device model
- `docs/VIDEO-SCRIPT.md` — optional re-record of the voice beat if the narrative shifts to on-device
- `todo.md`, `HANDOFF.md` — standard sprint bookkeeping
- `requirements.txt` — add `litert-lm` (and `ffmpeg-python` if Phase 1 confirms webm conversion is needed)

### Archived / closed

- `docs/plans/2026-04-12-audio-shim-decision.md` — link this roadmap's outcome back into Section 5 ("V2 roadmap") of that doc
- V2 item in `todo.md` — close as done or as rejected per Section 4 outcome

---

## 9. Open Questions (resolve before Phase 2)

1. Does LiteRT-LM expose thinking traces the way `GemmaClient.generate_with_thinking` does? If not, the confidence panel (Feature 4 in CLAUDE.md) does not apply to the audio path and that should be called out in ADR-011.
2. Is the model weights download redistributable under the Gemma license for a classroom-device install, or does each district need to download on first run? Affects `docs/RELEASE-READY.md`.
3. Do we need a per-request audio length cap enforced in `OnDeviceASR.transcribe` separate from the existing 10 MB byte cap in `capture.py` line 166? Recommendation: yes — cap at 30 s by default; teachers rambling for a minute is a UX signal, not a feature.
