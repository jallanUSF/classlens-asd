# ClassLens ASD — 5-Week Acceleration Plan
**Stack:** FastAPI (port 8001) + Next.js 16.2.2 | **Primary provider:** Google AI Studio `gemma-4-31b-it`
**GPU:** RunPod (development + demo recording) → Kaggle notebook (submission reproducibility artifact)
**Deadline:** May 18, 2026 | **Dev:** Jeff solo, Sarah as content/validation partner

---

## Situation audit

### What you have (strong)
- 5-agent sequential pipeline: Vision Reader → IEP Mapper → Progress Analyst → Material Forge → IEP Extractor
- Multimodal: worksheet photos + IEP PDF ingestion via Gemma vision
- Function calling: structured JSON extraction throughout
- Thinking mode: "Why is this an alert?" panel (Google provider only — correct)
- Bilingual parent comms: EN/ES/VI/ZH
- SSE streaming chat
- Precomputed demo data — demo never hangs on already-seen inputs
- 71 tests passing

### What's missing vs. judge criteria (gaps)
| Gemma 4 headline feature | Status | Gap size |
|---|---|---|
| Multimodal vision | Used | — |
| Function calling | Used | — |
| Thinking mode | Used (alerts only) | Partial |
| Long context (256K) | **Not used** | Large |
| Audio input (E2B/E4B) | **Not used** | Large |
| Ollama / local-first story | Wired; runs on RunPod GPU during dev | Submission notebook needed |

### Scoring math reality check
- Impact & Vision: **40 pts** — video only. This is the whole ballgame.
- Video Pitch: **30 pts** — also video.
- Technical Depth: **30 pts** — code + writeup verifies it's real.

70% of scoring is Sarah on camera, not code. Every feature decision should be filtered through: "Does this create a better video moment AND verify as technically real?"

---

## What NOT to add
Cutting scope is the plan:
- No new material types — 7 is already comprehensive
- No database — JSON files are correct for the demo scale
- No UI redesign — ship working features, not polish
- No fine-tuning — 5 weeks, solo; time is the constraint regardless of GPU access
- No new agents for minor tasks — extend existing ones

---

## Four features to add (priority order)

---

### Feature 1 — Long-context goal trajectory report
**Effort:** 2 days | **Prize impact:** Main track + Future of Education | **Gemma 4 feature:** 256K context

**What it is:**
Load a student's full semester of trial data — all captured artifacts, all IEP mapper outputs, all alert history — into a single Gemma 31B call. Ask it to analyze goal-by-goal trajectory: on track, at risk, or stalled, with a plain-English explanation and a suggested IEP meeting talking point.

**Why it wins:**
This is the only IEP tool in existence that can do this. No competing product ingests 6 months of granular trial data and synthesizes it in one call. It's a headline Gemma 4 capability (long context) that directly addresses the "wow factor" criterion. In the video it's the climactic moment: "Six months of Emma's data. Thirty seconds. Three talking points for next week's IEP meeting."

**Video moment:** Sarah sits at her laptop the night before an IEP review meeting. Opens ClassLens. Clicks "Generate Trajectory Report." Reads the three-sentence summary. Closes the laptop. Walks out the door on time.

**Implementation:**

New file: `agents/trajectory_analyst.py`
```python
async def analyze_trajectory(student_id: str, student_data: dict) -> dict:
    """
    Builds a long-context prompt from all trial data, alert history,
    and IEP goals for one student. Calls Gemma 31B with thinking mode.
    Returns per-goal trajectory objects: status, trend, confidence, suggestion.
    """
```

New endpoint: `POST /api/students/{student_id}/trajectory`
- Aggregates all `data/students/{id}/trials/*.json` + `data/students/{id}/alerts/*.json`
- Concatenates into structured long-context prompt (easily fits in 256K for demo data)
- Returns `{ goals: [{ goal_id, status, trend_summary, confidence, iep_meeting_note }] }`

New frontend component: `GoalTrajectoryCard.tsx`
- Shows per-goal status badge (On Track / At Risk / Stalled) with colored dot
- Expands to show trend summary + IEP meeting talking point
- One "Download as PDF" button for the teacher to bring to the meeting

**Precompute:** Add to `data/precomputed/` for the demo's primary student so it never waits.

---

### Feature 2 — Ollama prize shot: RunPod now, Kaggle notebook for submission
**Effort:** 1 day | **Prize impact:** Ollama Special Technology Track ($10,000) | **No code change needed**

**What it is:**
Not a feature — a two-phase demo strategy. The Ollama special prize awards $10K for the "best project that utilizes and showcases the capabilities of Gemma 4 running locally via Ollama." ClassLens already has Ollama wired in (`MODEL_PROVIDER=ollama`). The path that past hackathon winners use — and the correct sequence here — is:

**Phase 1 (now through week 4): Develop and record on RunPod.**
RunPod provides the GPU that makes `gemma4:e4b` via Ollama run at demo-viable speed (~50-80 tok/s). This is where all development happens and where the demo video gets recorded. RunPod IS Ollama — it's just Ollama on rented GPU hardware rather than a local machine. That's architecturally equivalent and fully honest in the writeup.

**Phase 2 (week 5): Kaggle notebook as the reproducibility artifact.**
The notebook's job is not to be the recording environment — it's to prove to judges that the demo video isn't smoke and mirrors. Create `kaggle_demo.ipynb` that:
1. Installs Ollama and pulls `gemma4:e4b` on a Kaggle T4 GPU
2. Starts ClassLens backend with `MODEL_PROVIDER=ollama`
3. Exposes it via a Cloudflare Quick Tunnel (`cloudflared tunnel --url http://localhost:8001` — no account needed)
4. Runs the smoke test suite so judges can verify it live

This is the public code repository + live demo attachment. Judges who want to verify can run it. The notebook doesn't need to be where you built — it needs to prove reproducibility. That's the distinction.

**Important timing note:** Don't wait until week 5 to test the Kaggle notebook. Spin it up during week 2 to verify that `gemma4:e4b` runs at acceptable speed on Kaggle's T4 and that the tunnel + smoke test works. Lock the notebook structure then. The last thing you want is a Kaggle GPU quota issue eating into submission week.

**RunPod cost tip:** Pin to a specific pod template so Ollama setup and model weights persist between sessions. Cold-pulling `gemma4:e4b` every session wastes time and money.

**Writeup framing:**
"ClassLens runs in two modes: cloud mode via Google AI Studio for schools with reliable internet, and local mode via Ollama for schools where student data must never leave the building. Development and demo recording used RunPod GPU infrastructure running Ollama. The attached Kaggle notebook reproduces the full local deployment on a T4 GPU, establishing that on-device deployment is architecturally complete — not theoretical."

This maps to the Digital Equity track: rural and under-resourced schools often have privacy policies that prohibit cloud processing of student data. Local Ollama is the answer to that.

**Steps:**
- Record demo video on RunPod (week 4, after features are complete)
- `kaggle_demo.ipynb` — Ollama install, model pull, uvicorn start, cloudflared tunnel, smoke test
- Document `MODEL_PROVIDER` env var switch in README with both modes
- Include 30-second "local mode" clip in the video showing it running

---

### Feature 3 — Teacher voice note → trial data entry
**Effort:** 2-3 days | **Prize impact:** Digital Equity + Future of Education | **Gemma 4 feature:** Audio (E2B/E4B)

**What it is:**
Teacher records a 15-30 second voice observation note in the browser. Gemma E4B (audio-capable) transcribes it and extracts structured trial data — goal ID, accuracy count, behavior observation — returning the same JSON schema that the Vision Reader produces. The teacher reviews the auto-filled form and taps submit.

**Why it wins:**
This is the strongest video moment in the deck. Show Sarah managing 8 students, hands full, dictating into her phone: "Marcus completed the coin sort. Got 4 out of 5. He was dysregulated in the first 5 minutes but recovered well." Cut to: structured progress note, auto-attached to Marcus's IEP goal, waiting for her review. That 20-second clip explains the equity story better than any paragraph.

It also exploits audio input — one of Gemma 4's headline multimodal capabilities not yet in the app.

**Implementation:**

Frontend: `VoiceCapture.tsx`
- Browser `MediaRecorder` API → captures webm/opus
- Simple record/stop/preview/submit UI (3 buttons)
- Converts to base64, sends to backend

Backend: `POST /api/capture/voice`
```python
async def capture_voice(student_id: str, audio_b64: str, media_type: str):
    """
    Sends audio to Gemma E4B via Google AI Studio audio input.
    Returns same schema as /api/capture (vision reader output):
    { goal_id, trial_count, accuracy, observation_text, confidence }
    """
```

New agent or extension: `agents/voice_reader.py`
- Constructs Gemma API call with audio part (Google AI Studio supports audio in multimodal content)
- System prompt matches Vision Reader's output schema so IEP Mapper receives identical input regardless of capture method
- Falls back to text-only extraction if audio transcription fails (whisper-style fallback not needed — if Google API is up, audio works)

**Provider note:** Audio input via Gemma E4B requires `google` provider. Document this clearly. For `ollama` and `openrouter`, the endpoint accepts text input instead (teacher types the note). The capability degrades gracefully.

**Precompute:** Pre-record 2-3 sample voice notes that map to existing student profiles. Store in `data/sample_voice/`. These are the demo assets Sarah records.

---

### Feature 4 — Safety & Trust confidence panel (extend thinking trace)
**Effort:** 1 day | **Prize impact:** Safety & Trust impact track ($10,000) | **Gemma 4 feature:** Thinking mode extended

**What it is:**
The "Why is this an alert?" thinking trace already exists and works. Extend it to all Material Forge outputs — not just alerts. Every generated material (lesson plan, social story, parent letter, etc.) shows:
- A confidence level badge: High / Review Recommended / Flag for Expert
- A collapsed reasoning panel: "Gemma's reasoning" (the thinking trace)
- A "Flag for review" button that adds a note to the student file

**Why it wins:**
The Safety & Trust impact track ($10K) explicitly rewards "frameworks for transparency and reliability, ensuring AI remains grounded and explainable." ClassLens already has the infrastructure. This is one day of wiring it to a new UI surface and writing the badge logic.

**In the video:** Teacher receives a social story for a new student. She hovers over the confidence badge — "Review Recommended." She clicks "Why?" — Gemma's reasoning: "Limited data on this student's communication level. Social story is based on ASD Level 2 defaults. Please verify with observation data." Teacher edits one sentence and marks it reviewed. This moment communicates: ClassLens doesn't replace teacher judgment. It supports it.

**Implementation:**

Backend: Modify `agents/material_forge.py`
- Switch all calls to `generate_with_thinking` (already exists in `gemma_client.py`)
- Add `confidence_score: "high" | "review_recommended" | "flag_for_expert"` to material output schema
- Logic: based on (a) whether student has >N prior observations, (b) whether thinking trace contains hedge language ("unclear", "limited data", "unable to determine")

Frontend: Update `MaterialViewer.tsx`
- Add confidence badge above each material card
- Collapsible reasoning panel (already exists in `AlertBanner.tsx` — copy the pattern)
- "Flag for review" button → `POST /api/materials/{id}/flag`

**That's it.** One day. This completes the Safety & Trust track argument.

---

## Prize targeting summary

| Prize | Amount | Current coverage | After 4 features |
|---|---|---|---|
| Main track (placement TBD) | up to $50K | Strong | Stronger |
| Future of Education | $10K | Solid | + Trajectory = stronger |
| Digital Equity & Inclusivity | $10K | Bilingual + ASD angle | + Voice + Ollama = much stronger |
| Safety & Trust | $10K | Alert thinking trace only | + Confidence panel = full coverage |
| Ollama special | $10K | Runs on RunPod GPU (Ollama backend, MODEL_PROVIDER=ollama) | + Kaggle notebook = prize-eligible |

**Accessible total with strong execution: $80-90K if Main Track places 2nd or 3rd.**

---

## Build order (5 weeks)

| Week | Feature | Why this order |
|---|---|---|
| Week 1 | Feature 1 — trajectory report | Highest judge impact, no external dependency, sets long-context story |
| Week 2 | Feature 2 — Kaggle notebook (test early, lock structure) | One day. Verify T4 speed + tunnel. Remainder: commit the 5 unstaged features. |
| Week 3 | Feature 3 — voice note capture | Best video footage, needs Sarah to record samples |
| Week 4 | Feature 4 — confidence panel | One day of work, then rest of week: integration testing + demo polish |
| Week 5 | Video, writeup, submission | **Gate this hard. No new features in week 5.** |

---

## Video story arc (3 minutes, 70% of scoring)

**Hook (0:00–0:25):** Sarah on camera. "I have 8 students with autism. Each one has an IEP with 4-6 goals. Every day I collect data on all of them. And every night I manually enter it, write notes, and try to remember who's falling behind." Cut to: stack of worksheets. Clock showing 4:45pm.

**The capture (0:25–0:55):** Sarah takes a photo of a worksheet. ClassLens parses it in seconds. She then records a 20-second voice note about the session. Structured trial data populates automatically. "That used to take 15 minutes. Per student."

**The insight (0:55–1:30):** She opens Emma's profile. Clicks "Generate Trajectory Report." Gemma analyzes 6 months of data. "Goal 3 — coin identification — is stalled at 62% for 3 weeks. Recommended: adjust the practice format before the IEP meeting Thursday." Sarah reads it. "That's exactly what I noticed. I just didn't have the words for it."

**The trust moment (1:30–1:55):** She hovers over a social story for a new student. "Review Recommended." Clicks "Why?" — Gemma's reasoning appears. She makes one edit. "I'm still the teacher. ClassLens is my assistant."

**The materials (1:55–2:20):** One click. Parent letter in Vietnamese for Marcus's family. Social story for tomorrow. Tracking sheet for the aide. "I used to spend Sunday evenings doing this. Now I don't."

**The close (2:20–3:00):** "ClassLens ASD. Built for the teachers who show up every day — and the students who deserve their full attention."

---

## Writeup structure (1,500 word limit, ~30 pts of scoring)

1. **The problem** (~200 words) — ASD teacher burnout, IEP documentation burden, data entering instead of teaching. Cite CDT 57% stat.
2. **ClassLens ASD** (~100 words) — one-sentence product description, target user, core promise.
3. **Architecture** (~400 words) — 5 agents, sequential pipeline, provider abstraction. Diagram or table. Emphasize: no LangChain, direct Gemma 4 API, real function calling, real thinking mode.
4. **Gemma 4 capabilities used** (~300 words) — Multimodal (vision + audio), function calling, thinking mode, long context. One paragraph each. Be specific about which model size and which API call type.
5. **Local deployment / privacy** (~150 words) — Ollama path, why it matters for schools, Kaggle notebook as proof.
6. **What we learned** (~200 words) — Thinking mode only reliable on Google provider (honest engineering note judges will respect). CPU Ollama speed constraint. How precomputed data enables reliable demos without faking results.
7. **Impact and next steps** (~150 words) — Sarah's input, real classroom validation, what deployment would look like.

**Cite:** Waterfield et al. (2025) Journal of Special Education Technology. CoIEP / Zhang et al. (2025) University of Wyoming. These give the writeup academic credibility that most hackathon submissions lack.

---

## CLAUDE.md additions for this sprint

```
## Sprint additions (weeks 1-4 only)

### Feature 1 — trajectory_analyst.py
- New file at agents/trajectory_analyst.py
- New router at routers/trajectory.py, mount at /api/students/{id}/trajectory
- Aggregates data/students/{id}/trials/ + data/students/{id}/alerts/
- Single Gemma call: MODEL=gemma-4-31b-it, thinking=True, long context
- Output schema: { goals: [{ goal_id, status, trend_summary, confidence, iep_meeting_note }] }
- Add precomputed result to data/precomputed/trajectory_{student_id}.json

### Feature 2 — Kaggle notebook
- New file: kaggle_demo.ipynb at repo root
- Installs: ollama, runs pull gemma4:e4b, starts uvicorn with MODEL_PROVIDER=ollama
- Uses cloudflared tunnel (no auth required)
- Smoke test: hits /api/students, /api/capture with precomputed image

### Feature 3 — voice_reader.py
- New file at agents/voice_reader.py
- New endpoint at routers/capture.py: POST /api/capture/voice
- Output schema: identical to vision_reader output (IEP Mapper receives same input either way)
- Provider guard: if MODEL_PROVIDER != 'google', return {"error": "audio_not_supported", "fallback": "text_input"}
- Frontend: VoiceCapture.tsx — MediaRecorder + base64 encoding + review step before submit
- Sample assets: data/sample_voice/sample_1.webm through sample_3.webm (Sarah records these)

### Feature 4 — confidence panel
- Modify agents/material_forge.py: all generate() calls → generate_with_thinking()
- Add confidence_score to MaterialOutput schema (pydantic): Literal["high", "review_recommended", "flag_for_expert"]
- Confidence logic: high if student has >5 prior trials AND thinking trace has no hedge terms
- Frontend: extend MaterialViewer.tsx — copy AlertBanner.tsx thinking trace panel pattern exactly
- New endpoint: POST /api/materials/{id}/flag → appends to data/students/{id}/flags.json

## Don't touch in sprint
- Agent architecture (no new agents)
- Auth / user system
- Database migration
- UI redesign
- Video / submission work (week 5 only)
```
