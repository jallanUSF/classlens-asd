# Architecture Decision Record: ClassLens ASD
## Gemma 4 Good Hackathon Entry — Technical Depth (30% scoring)

**Project:** Multi-agent AI system for IEP tracking & adaptive material generation
**Deadline:** May 18, 2026 | **Competition:** Kaggle Gemma 4 Good Hackathon ($200K prize pool)
**Scoring:** Technical Depth = 30% | Impact & Vision = 40% | Video = 30%

---

## ADR-001: Model Selection — Gemma 4 27B-A4B-it via Google AI Studio

**Context:**
Competition requires Gemma 4; free tier budget ($0); need multimodal reasoning (IEP documents + student work samples) + agentic function calling (tool use for retrieval, file I/O).

**Decision:**
Use **Gemma 4 27B-A4B-it** via **Google AI Studio REST API** (free tier).

**Rationale:**
- **27B over smaller variants:** 27B provides multimodal understanding (vision transformer backbone), structured output via function calling, and reasoning depth required for IEP analysis. 9B/14B lack stable function calling.
- **Google AI Studio over Vertex AI:** Zero-cost free tier (15 RPM limit acceptable for demo). Vertex requires GCP project + billing setup. Studios simple API key auth reduces friction for judges verifying code.
- **Gemma 4 mandatory** (competition requirement). Demonstrates commitment to open-weight models vs proprietary APIs.

**Trade-offs:**
| Aspect | Choice | Alternative | Cost |
|--------|--------|-------------|------|
| Model | Gemma 4 27B | GPT-4o / Claude | Violates competition rules |
| API | Google AI Studio | Vertex AI | Higher setup friction |
| Rate limit | 15 RPM | Unlimited (paid) | Mitigated via pre-baked demo |

**Status:** ✅ DECIDED

---

## ADR-002: Multi-Agent Architecture vs Monolithic Prompt

**Context:**
IEP analysis requires: (1) document understanding, (2) goal-to-progress mapping, (3) pattern detection, (4) material synthesis. Single prompt runs out of context window; agent orchestration adds complexity but improves modularity & judge transparency.

**Decision:**
4-agent pipeline: **Vision Reader → IEP Mapper → Progress Analyst → Material Forge**

**Rationale:**
- **Separation of concerns:** Each agent has single responsibility; failure in one stage doesn't corrupt others.
- **Context window efficiency:** Sequential processing avoids "throw everything at once" bloat.
- **Judge visibility:** Explicit agents demonstrate agentic reasoning — core Gemma 4 strength vs simple API wrappers.
- **Why not LangChain/LangGraph/CrewAI?** Direct API calls offer:
  - Full control over prompting (no abstraction hiding the Gemma reasoning)
  - Judges see raw Gemma API usage, not framework glue
  - Fewer dependencies = easier deployment on Streamlit Community Cloud
  - Hackathon timeline: framework setup overhead not worth it

**Agent breakdown:**
1. **Vision Reader** → Extracts text + structure from IEP PDFs via `vision_analyze` tool
2. **IEP Mapper** → Parses goals, benchmarks, accommodations into JSON schema
3. **Progress Analyst** → Detects patterns in student work samples; gap analysis vs goals
4. **Material Forge** → Generates differentiated materials (3 audiences, 7 output types)

**Trade-offs:**
| Aspect | Multi-Agent | Monolithic | Impact |
|--------|------------|-----------|--------|
| Context | ~4K per agent | ~12K single prompt | Multimodal clarity |
| Transparency | Explicit stages | Black box | Judge scoring (Technical Depth +5) |
| Latency | ~4-6s total | ~2-3s | Within demo tolerance |
| Code complexity | ~300 LOC orchestration | ~200 LOC prompting | Worth the clarity |

**Status:** ✅ DECIDED

---

## ADR-003: Pre-Baked Demo Mode with Cached Results

**Context:**
Free tier: 15 RPM limit. Live demo during judging (unknown timing) + multiple submission videos require repeated API calls. Risk: rate limit exceeded mid-demo = bad judge experience.

**Decision:**
Implement **cached demo mode** (JSON fixtures) + real-time toggle for live API calls.

**Rationale:**
- **Rate limit resilience:** Pre-computed agent outputs for 3 student profiles guarantee smooth judging demo.
- **Reproducibility:** Same results every demo run = consistent narrative for 10-minute video & live showcase.
- **Judge UX:** 3-second Material Forge output > 30-second API wait (perceived performance).
- **Authenticity:** Toggle between demo & live modes in UI. Judges can see:
  - Real Gemma API call latency (if time permits)
  - Actual cached outputs (shows pipeline execution without rate limit risk)

**Cache structure:**
```
cache/
  ├── student_alice.json  # Complete agent outputs (Vision → Material Forge)
  ├── student_bob.json
  └── student_carol.json
```

**Trade-offs:**
| Aspect | Cached Demo | Pure Live API | Risk |
|--------|-----------|---------------|------|
| Judge experience | Instant (<1s) | 30-60s wait | Cached wins (demo > latency) |
| Authenticity | "Warmed" results | 100% live | Judges see reasoning quality, not speed |
| Effort | ~6 hours pre-compute | ~0 extra | Worth the UX polish |

**Implementation note:** Cache timestamps + API endpoint transparency in UI footer ("Demo Mode: Using cached results from Apr 3. [Run Live]")

**Status:** ✅ DECIDED

---

## ADR-004: State Management — JSON + Pydantic vs Database

**Context:**
Hackathon scope: 3-5 student profiles, ~10 IEP documents, ~50 work samples. Single-instance deployment (Streamlit Cloud). No concurrent users or persistence requirements.

**Decision:**
**JSON files + Pydantic** (no database).

**Rationale:**
- **Simplicity:** 3 files (IEP metadata, progress records, material history) = no DB setup, no migrations, no secrets management.
- **Pydantic validation:** Type safety + schema documentation (judges see clean data structures).
- **Git-friendly:** All state is static files; easy for judges to inspect, reproduce, or fork.
- **Deployment:** Streamlit Cloud reads JSON, zero external dependencies.
- **Judges' perspective:** "Pulls one GitHub repo, runs `streamlit run app.py`, works immediately" = 👍

**Schema examples:**
```python
class IEPProfile(BaseModel):
    student_id: str
    goals: List[Goal]
    accommodations: List[str]
    progress_records: List[ProgressRecord]  # PDF-extracted data

class MaterialOutput(BaseModel):
    type: Literal["social_story", "visual_schedule", "adapted_lesson", ...]
    audience: Literal["student", "teacher", "parent"]
    content: str
    source_goal_id: str
```

**Trade-offs:**
| Aspect | JSON + Pydantic | SQLite / PostgreSQL | Scalability |
|--------|-----------------|-------------------|------------|
| Setup time | 1 hour | 4 hours | Hackathon critical |
| File size limit | ~100MB | Unlimited | 50 samples ≈ 5MB total |
| Concurrent writes | No | Yes | Irrelevant (single demo) |
| Audit trail | Git history | DB logs | Git sufficient |

**Future migration:** If expanding post-hackathon, Pydantic models are database-agnostic (easy SQLAlchemy swap).

**Status:** ✅ DECIDED

---

## ADR-005: Deployment — Streamlit Community Cloud

**Context:**
Free hosting requirement; need public URL for judges + video demo; simple CI/CD for rapid iterations (deadline May 18).

**Decision:**
**Streamlit Community Cloud** (deploy directly from GitHub).

**Rationale:**
- **Zero cost:** Streamlit Community Cloud is free tier. Vercel/AWS cost $ or require credits.
- **Native Streamlit:** Built for Python + data apps. Judges see their browser → no installation friction.
- **1-click deploy:** GitHub push → auto-redeploy. Perfect for pre-submission updates.
- **Public URL:** Can embed in Kaggle submission + video description.
- **Why not AWS/GCP/Vercel?**
  - AWS: Free tier expired after 12 months (risky for May 2026 deadline)
  - Vercel: Designed for Next.js; Streamlit adapter = extra complexity
  - Custom VPS: Requires ops work (DNS, SSL, monitoring) = time away from features

**Deployment pipeline:**
```
Local dev (Python 3.11)
  ↓
Git push to GitHub
  ↓
Streamlit Cloud auto-detects `requirements.txt`
  ↓
App live in ~90 seconds
  ↓
Logs + performance visible in Streamlit dashboard
```

**Secrets management:** Google AI Studio API key in Streamlit Secrets (encrypted in cloud, injected at runtime).

**Trade-offs:**
| Aspect | Streamlit Cloud | AWS | Vercel | Custom |
|--------|-----------------|-----|--------|--------|
| Cost | $0 | $0* (*expires) | $0-5/mo | $5-50/mo |
| Deploy time | 90s auto | 10min manual | 60s | 5min+ manual |
| Simplicity | Built-in | Config heavy | Adapter needed | DIY |
| Judge experience | 1-click web | VPC setup | Works | Works |

**Status:** ⚠️ SUPERSEDED by ADR-010 — Now deploying Next.js frontend to Vercel (free) and FastAPI backend to Railway/Render (free tier). See ADR-010 for rationale.

---

## ADR-006: Multi-Track Prize Strategy — Primary + Ollama Edge Track

**Context:**
Kaggle competition offers **4 prize tracks:** Main ($50K), Education ($10K), Ollama Special Tech ($10K), Digital Equity ($10K). Each has different judging criteria but accepts same submission.

**Decision:**
Primary submission: **Gemma 4 27B via Google AI Studio** (maximize Technical Depth scoring).
Secondary track demo: **Gemma 4 E4B via Ollama** (edge device inference proof-of-concept).

**Rationale:**
- **Primary (Main track):** Gemma 4 27B on free GPU tier demonstrates "full power" reasoning for IEP analysis. Score: Impact (40) + Video (30) + Technical Depth (30, cloud API).
- **Education track alignment:** IEP/ASD education use case = natural fit ($10K secondary prize).
- **Ollama edge demo:** Competitors who deploy on edge miss this. We show:
  - Gemma 4 E4B (quantized 4-bit) running on laptop CPU (~2B parameters)
  - Same agent pipeline, degraded but functional (latency trade-off = acceptable for offline school districts)
  - Judges see **Technical Depth x2:** cloud + edge strategies = differentiation
- **Digital Equity track:** Offline capability = schools with limited internet connectivity.

**Ollama approach:**
```
Main app (27B cloud API):
  → Link to "Edge Mode" (E4B local Ollama)
  → Same Streamlit UI
  → Same Material Forge outputs
  → Slower (tolerable for offline schools)
```

**Trade-offs:**
| Track | Submission | Gemma variant | Latency | Scoring gain |
|-------|-----------|---------------|---------|----|
| Main | Cloud API | 27B | 5-10s | +30 (Tech Depth) |
| Education | Same code | 27B | 5-10s | +10 (Education award) |
| Ollama | Code + guide | E4B local | 20-60s | +10 (Tech award) + differentiation |
| Digital Equity | Documentation | E4B local | 20-60s | +10 (Equity award) |

**Implementation:** Single codebase with `--mode cloud` vs `--mode ollama` flag. Video shows both.

**Status:** ✅ DECIDED

---

## ADR-007: Material Forge Output Design — 7 Types × 3 Audiences

**Context:**
IEP material generation is core differentiator. Teachers need actionable, diverse outputs. Generic "generate text" = weak; specific, structured outputs = strong for impact scoring.

**Decision:**
**7 output types** (student-facing + teacher-facing + parent-facing):

1. **Social Story** (Carol Gray framework) — Student
2. **Visual Schedule** (pictorial sequence) — Student
3. **Adapted Lesson** (differentiated content) — Teacher
4. **Accommodation Checklist** (task breakdown) — Teacher
5. **Parent Communication** (progress summary) — Parent
6. **Sensory Profile** (needs-based activities) — Student + Teacher
7. **IEP Goal Tracker** (progress visualization) — Teacher + Parent

**Rationale:**
- **Carol Gray social stories:** Evidence-based autism intervention framework. Shows research grounding vs ad-hoc generation.
- **3 audiences:** Students (concrete, visual), Teachers (actionable), Parents (transparent). Demonstrates user-centered design.
- **Why these 7?**
  - IEP goals → Adapted Lesson (core teaching tool)
  - Accommodations → Checklist (compliance + implementation)
  - Social-emotional needs → Social Story + Sensory Profile (evidence-backed)
  - Progress tracking → Goal Tracker (measurement)
  - Parent engagement → Communication template (often missing in edtech)
- **Structured JSON output:** Each material includes:
  ```json
  {
    "type": "social_story",
    "student_name": "Alice",
    "goal_id": "G001",
    "audience": "student",
    "content": "...",
    "frameworks_applied": ["Carol Gray social stories"],
    "difficulty_level": 2,  // 1-5 scale
    "estimated_reading_time_minutes": 3
  }
  ```

**Trade-offs:**
| Aspect | 7 specific types | 3 generic templates | Judge scoring |
|--------|-----------------|-------------------|---|
| Specificity | High (ASD-tailored) | Generic (any disability) | +Impact: teacher value |
| Implementation | ~600 LOC prompts | ~100 LOC templates | Complexity worth it |
| Generalization | Lower | Higher | Acceptable (target market = K-12 ASD) |
| Research backing | Evidence-based | Ad-hoc | +Technical Depth |

**Status:** ✅ DECIDED

---

## ADR-008: Error Handling & Fallback Strategy

**Context:**
Free tier API limits + network failures possible during live demo. User experience must graceful degrade.

**Decision:**
3-tier fallback:
1. **Cache hit** (preferred) → Instant cached result
2. **API success** → Real Gemma output
3. **API failure** (rate limit / timeout) → User-friendly error + cache suggestion

**Implementation:**
```python
def run_agent(profile_id: str, agent_type: str) -> dict:
    # Tier 1: Try cache first
    cached = load_cache(profile_id, agent_type)
    if cached:
        return {"source": "cache", "data": cached}

    # Tier 2: Try live API
    try:
        result = call_gemma_api(profile_id, agent_type)
        return {"source": "api", "data": result}
    except RateLimitError:
        # Tier 3: Fallback + user message
        return {
            "source": "cached_fallback",
            "data": load_cache(profile_id, agent_type),
            "message": "⚠️ Rate limited. Showing cached results from Apr 3."
        }
```

**Status:** ✅ DECIDED

---

## ADR-009: Testing Strategy — Fixtures Over Live Tests

**Context:**
Free tier rate limits make continuous live testing impractical. Need reproducible test suite for judges & code review.

**Decision:**
**Fixture-based unit tests** (mock Gemma responses) + **1 integration test** (live API smoke test, run weekly pre-competition).

**Rationale:**
- **Fixtures:** `test/fixtures/agent_vision_reader_output.json` contains real Gemma outputs from Apr 1. Tests verify:
  - Pydantic schema validation
  - IEP Mapper parsing
  - Material Forge formatting
  - No API call needed
- **Integration test:** `test/integration_smoke.py` (weekly run via GitHub Actions) validates API endpoint is alive + quota available.
- **Judge confidence:** Tests run in CI on every push. Badge in README = "code quality assured."

**Trade-offs:**
| Approach | Fixtures | Live tests | CI/CD reliability |
|----------|----------|-----------|---|
| Speed | Instant | 30s (API latency) | Fast feedback |
| API quota | Zero | Consumes quota | Fixtures win |
| Real-world fidelity | 95% (fixture = real output) | 100% | Acceptable trade-off |

**Status:** ✅ DECIDED

---

## ADR-010: Replaced Streamlit with Next.js 16 + FastAPI

**Context:**
The original prototype used Streamlit for the UI layer. While Streamlit enabled rapid prototyping, it introduced significant limitations as the app matured:
- **Narrow single-column layout:** Streamlit's layout model doesn't support a true multi-column application shell. Our design required a three-column layout (student sidebar, content area, chat panel) that Streamlit cannot achieve without fragile hacks.
- **Session state quirks:** Streamlit reruns the entire script on every interaction. State management for multi-step workflows (upload → transcription → mapping → material generation) required constant workarounds with `st.session_state`.
- **Limited component control:** Custom material renderers (lesson plans, social stories, admin reports) needed precise formatting, print stylesheets, and interactive controls (approve/regenerate/print) that Streamlit's component model cannot support.
- **No mobile responsive design:** Streamlit has no responsive breakpoint system. Teachers need to use ClassLens from their phone in the classroom.
- **Deployment flexibility:** Streamlit Community Cloud is the only free option; it limits hosting control and doesn't support a separate API layer.

**Decision:**
Replace Streamlit with **Next.js 16 + React 19 + Tailwind CSS v4 + shadcn/ui** for the frontend, and **FastAPI** as a REST backend wrapping the existing Python agent pipeline.

**Architecture:**
```
Browser (Next.js 16)          FastAPI (Python)
┌─────────────────────┐      ┌─────────────────────┐
│ Three-column layout  │ ←→  │ /api/students        │
│ - Student sidebar    │      │ /api/capture         │
│ - Content area       │      │ /api/materials       │
│ - Chat panel         │      │ /api/progress        │
│ - MaterialViewer     │      │ /api/chat            │
│ - Mobile hamburger   │      │ /api/alerts          │
│   + chat FAB         │      └──────────┬──────────┘
└─────────────────────┘                  ↓
                              4-Agent Pipeline (unchanged)
                              Vision Reader → IEP Mapper
                              → Progress Analyst → Material Forge
```

**Key UI capabilities gained:**
- **Three-column layout:** Student sidebar (left), content area (center), chat panel (right) — all independently scrollable
- **MaterialViewer sheet:** Slides in from right, renders professional material output with Approve/Regenerate/Print buttons and "Teacher review required" footer
- **Six material renderers:** LessonPlanView, ParentLetterView, AdminReportView, SocialStoryView, TrackingSheetView, VisualScheduleView — each with purpose-built formatting
- **Print CSS:** `@media print` renders materials at letter size with clean typography, hiding all navigation chrome
- **Mobile responsive:** Sidebar becomes hamburger menu; chat panel becomes floating action button (FAB)
- **shadcn/ui components:** Accessible, composable primitives (Sheet, Accordion, Card, Badge) built on Radix UI

**Model provider flexibility:**
The FastAPI backend supports three model providers via a `MODEL_PROVIDER` environment variable:
- **Google AI Studio** (default) — free tier, 15 RPM
- **OpenRouter** — alternative access to Gemma 4 and other models, useful for failover
- **Ollama** — fully offline local inference for privacy-conscious schools

**Consequences:**

| Aspect | Benefit | Cost |
|--------|---------|------|
| UX quality | Professional three-column layout, MaterialViewer, print support | More complex stack (JS + Python) |
| Mobile support | Full responsive design with hamburger + FAB | Additional CSS/layout work |
| Material rendering | Six dedicated renderers with approve/print workflow | More components to maintain |
| Deployment | Vercel (frontend) + Railway/Render (backend) | Two services instead of one |
| Developer experience | Hot reload, TypeScript safety, component composition | Requires Node.js + Python environments |
| Agent pipeline | Completely unchanged — FastAPI wraps existing code | Thin REST layer to maintain |
| Judge experience | Professional, polished UI that demonstrates real product potential | N/A (net positive) |

**Trade-offs accepted:**
- **Stack complexity:** Two processes (Next.js dev server + FastAPI) instead of one `streamlit run`. Mitigated by clear README instructions and Docker Compose (future).
- **Deployment:** Two services to deploy. Mitigated by Vercel's zero-config Next.js deployment and Railway/Render's one-click Python deployment.
- **Learning curve:** Next.js + React + Tailwind is a larger surface area than Streamlit. Acceptable because the UI quality improvement directly impacts judge scoring (Video = 30 points).

**Why this was the right call:**
The video demo (30% of score) and live demo URL (judges try it themselves) are critical scoring moments. A Streamlit app with a narrow column layout and basic widgets communicates "prototype." A three-column Next.js app with professional material renderers, approve/print controls, and mobile responsive design communicates "product." For a $200K prize pool competition, the UI investment is worth the added complexity.

**Status:** ✅ DECIDED

---

## Summary: Technical Depth Scorecard

| Decision | Differentiator | Judge signal |
|----------|---|---|
| ADR-001: Gemma 4 27B (not smaller) | Multimodal reasoning | ✅ Thought-through |
| ADR-002: 4-agent pipeline (not monolithic) | Modularity + transparency | ✅ Architectural maturity |
| ADR-003: Cached demo mode | UX polish + rate limit strategy | ✅ Production thinking |
| ADR-004: JSON + Pydantic (no DB) | Pragmatic simplicity | ✅ Scope discipline |
| ADR-005: ~~Streamlit Cloud~~ → Vercel + Railway (ADR-010) | Zero friction deployment | ✅ Judge experience |
| ADR-006: Cloud + Ollama dual-track | Edge computing angle | ✅ Technical depth x2 |
| ADR-007: 7 structured outputs × 3 audiences | Research-backed (Carol Gray) | ✅ Impact focus |
| ADR-008: 3-tier fallback | Graceful degradation | ✅ Production resilience |
| ADR-009: Fixture tests + weekly smoke test | CI/CD transparency | ✅ Code quality |
| ADR-010: Next.js + FastAPI (not Streamlit) | Professional UX + mobile | ✅ Product maturity |

**Expected Technical Depth Score: 26-30 / 30** (judges see deliberate engineering choices, not YOLO hacking)

---

## Revision History

| Date | Version | Notes |
|------|---------|-------|
| 2026-04-04 | 1.0 | Initial ADR for submission |
| 2026-04-05 | 1.1 | Added ADR-010: Next.js + FastAPI replaces Streamlit |

---

**Document prepared for:** Kaggle Gemma 4 Good Hackathon Judges
**Last updated:** 2026-04-05
**Next review:** 2026-05-10 (pre-submission final check)
