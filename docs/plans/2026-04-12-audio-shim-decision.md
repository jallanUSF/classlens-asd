# Audio Shim Decision — Voice Capture

**Date:** 2026-04-12 (updated after spike)
**Owner:** Jeff
**Status:** **DECIDED — ship Option C for hackathon; Gemma 4 E4B on-device ASR on V2 roadmap**

---

## 1. Current state (post-spike)

`gemma-4-31b-it` on Google AI Studio returns HTTP 400 when an `audio/*` Part is attached. `gemma-3n-e4b-it` and `gemma-3n-e2b-it` on AI Studio also return 400 with the explicit message `"Audio input modality is not enabled for models/gemma-3n-e4b-it"` — Google gates audio off at the hosting layer for every Gemma variant they serve through AI Studio.

On `backend/routers/capture.py`, `_is_google_provider()` returns `False` by default (requires `VOICE_AUDIO_ENABLED=1`), so `POST /api/capture/voice/supported` reports `supported=false` and the `VoiceCapture.tsx` UI routes teachers directly to the typed-observation textarea. The round trip works end-to-end via `VoiceReader.transcribe_from_text` → `generate()`. This is the path we are shipping for the hackathon.

## 2. Options evaluated

| Option | Host | Effort | Spirit fit | Demo-day risk | Verdict |
|---|---|---|---|---|---|
| **A. Gemini transcription shim** (audio → `gemini-2.x-flash` → text → Gemma) | AI Studio | S (~half-day) | Mixed-model in critical audio path; invites "why Gemma?" | Low | Viable but weaker narrative |
| **B. Two-step Gemini→Gemma with prosody/sentiment annotations** | AI Studio | M (1–2 days) | Same concern as A, plus more surface | Medium | Not worth the extra day |
| **C. Text-only observation capture** (ship current behavior, drop mic from UI) | — | Trivial (copy + affordance changes only) | ✅ 100% Gemma family on critical path | Very low | **Chosen** |
| **D. Gemma 3n E4B/E2B via Vertex AI** | Vertex | M | Pure Gemma | Medium (new GCP infra on demo day) | Deferred — viable post-hackathon |
| **E. Gemma 4 E4B on-device via LiteRT-LM** (Google AI Edge Eloquent stack) | Local | **Blocked** on Windows | Best-in-class — "Gemma 4 E4B on-device for audio, 31B for reasoning" | N/A (blocked) | **V2 roadmap** |

### E. Spike findings (why it's V2, not V1)

- LiteRT-LM Python API is **Linux/macOS only** per Google's own docs: *"The Python API of LiteRT-LM for Linux and macOS (Windows support is upcoming)."* Dev machine is Windows Server 2022.
- `pip install litert-lm-api-nightly` on Windows → `No matching distribution found`. No Windows wheel published as of 2026-04-12.
- Local WSL is at WSL1, not WSL2. Usable path would require: WSL2 upgrade → Ubuntu install → nightly package → 3.65 GB model → Windows↔WSL2 HTTP bridge from FastAPI. Four stacked unknowns for a feature rated below Vision / Thinking / Podcast on judge impact.
- Documented Python example still references "Gemma 3n variants" for audio — Gemma 4 E4B audio via Python binding is ambiguous even on supported platforms.

**Conclusion:** Gemma ASR via LiteRT-LM is the architecturally right answer but not delivery-ready for May 18 on this hardware.

## 3. Decision: Option C

**Rationale.**
1. **Spirit of competition is strongest.** 100% Gemma 4 family on every intelligent call. No "why not pure Gemma?" for judges.
2. **Demo-day risk is lowest.** Zero new infra, zero new API dependency, zero live-mic-failure scenarios. The UI is already shipping today.
3. **The feature it replaces is realistic.** Teachers *already* type observations into data sheets; auto-populating IEP goals from typed text is the actual workflow improvement. The "voice" framing was a nice-to-have, not the core value prop.
4. **Saves sprint cycles** for the remaining open items: Sarah's content, Marcus Grade-0 cleanup, release-ready checklist, video recording.
5. **V2 has a real, credible path** — Gemma 4 E4B on-device via LiteRT-LM once Windows Python bindings ship — which the ADR will document as a deliberate architectural decision.

## 4. Ship changes (Option C implementation)

### UI (text-first)

| File | Change |
|---|---|
| `frontend/src/components/student/VoiceCapture.tsx` | Idle state: keyboard icon (not mic), copy "Type a quick observation. One or two sentences is plenty.", primary button "Type Observation", mic Record button only rendered when `audioSupported === true` (i.e., V2 / `VOICE_AUDIO_ENABLED=1`). Audio code paths preserved dormant. |
| `frontend/src/app/student/[id]/page.tsx` | Section title "Voice Observation" → "Quick Observation". Comment flags audio as V2. |
| `VoiceCapture.tsx` done-state label | "Voice observation captured" → "Observation captured". |

### Backend (no change required)

`_is_google_provider()` gate already defaults off. MediaRecorder code in VoiceCapture remains intact so a single flag flip re-enables it once the V2 audio path is wired.

### Component name

Keep `VoiceCapture.tsx` as the filename (git history, imports) but treat the component as "Observation Capture" in all user-facing copy. Rename in a post-hackathon cleanup pass — renaming files during the sprint adds merge-conflict risk for no user-visible gain.

## 5. V2 roadmap (post-hackathon)

Primary: **Gemma 4 E4B on-device via LiteRT-LM.** Watch for:
- Windows Python bindings for `litert-lm` (currently "upcoming")
- Gemma 4 E-series audio confirmed through the Python API (docs currently ambiguous — may require Gemma 3n E4B as interim)
- Offline-first story is a genuine FERPA win for school deployments — no student audio ever leaves the classroom device

Secondary fallback if LiteRT-LM stays blocked on Windows:
- Vertex AI Gemma 3n E4B (paid, but pure Gemma, no vendor-lock-in story issue)

Not chosen: Gemini shim (option A). If we do add voice post-hackathon, we add it *as pure Gemma*, not as a mixed-model shortcut.

## 6. Rejection criteria — back out only if

- Sarah reviews the typed-observation UX and it is genuinely unusable for teachers in-the-moment → reopen decision, pick A as a tactical unblock.
- Judge-facing framing requires a voice demo moment that can't be delivered any other way → pre-record a narrated voice clip in the 3-min video rather than building a live path.

## 7. Artifacts to update

- `todo.md` — close item 1 ("audio model decision"), add V2 item
- `HANDOFF.md` — note decided + shipped
- `docs/ADR.md` — add decision entry: "Voice input: text-first in V1; Gemma 4 E4B on-device ASR in V2"
- `docs/VIDEO-SCRIPT.md` — check for mic-dependent beats; rewrite as typed observation if present
- `docs/RELEASE-READY.md` — codify `VOICE_AUDIO_ENABLED=0` as the shipping default (already reflected per subagent draft)
