# ClassLens ASD

**Gemma 4 Good Hackathon — Kaggle Submission**

> A multi-agent system that turns a photo of student work into IEP-aligned progress data and personalized intervention materials — built on Gemma 4, co-designed with a working special education teacher, tested in a real classroom.

---

## 1. Friday afternoon in a rural Idaho classroom

It is 4:15 PM. The last bus has left. Sarah is a 15-year special education teacher with ten students across grades 1–5, all with moderate-to-severe autism. Her desk is covered with the week's evidence of learning: writing samples, AAC printouts, photos of drawings from her phone, a stack of behavior tracking sheets, and a half-finished stack of handwritten progress notes for each student's IEP file. A tired iPad is playing her son's dinosaur playlist on loop because her husband is picking him up late.

Between 4 and 7 PM every Friday, she hand-transcribes student work into IEP trackers, hand-writes four to six progress notes, drafts multilingual emails to parents, and builds Monday's visual schedules from scratch. By six, Monday's lesson plans are still unwritten. This is not unusual. This is the week.

Sarah spends **5 to 7 hours every week on IEP paperwork alone** — roughly an entire workday — before she gets to lesson planning, parent communication, or the professional reading she needs to stay current. It is not a failure of effort. It is a tooling failure: the software her district provides was built for compliance and storage, not for the messy, multimodal reality of evidence in a classroom where a third of her students don't write and half communicate through a device.

ClassLens ASD exists because of Friday afternoons. We watched one special education teacher drown in evidence that couldn't be turned into insight without an hour of manual re-entry per student per week. Gemma 4 is the first open foundation model we found that could close that gap at the point of instruction — multimodal vision for the worksheet, function calling for the IEP goal match, thinking mode for the "is this a real trend or just a noisy Monday."

This is not a research project. This is the tool we built for Sarah.

---

## 2. The gap we are closing

Existing IEP platforms (Skyward, Infinite Campus, PowerSchool) are digital filing cabinets. They handle **storage** and **compliance checklists**. None of them:

- **Read student work directly.** A photo of a child's handwriting, a drawing, an AAC device screen — evidence produced dozens of times a day — never enters the IEP system except as a teacher's manually-typed summary.
- **Map evidence to goals automatically.** Every piece of evidence has to be hand-classified against that student's specific IEP goals before it becomes trackable progress data.
- **Surface real trends.** With 4–8 data points per goal per quarter, noise and signal are hard to separate. Teachers rely on gut feel because the tools offer no help.
- **Generate personalized intervention materials.** Lesson plans, social stories, tracking sheets, and parent communications all have to be built by hand, for each student, every week.
- **Serve special populations with accessibility-first design.** Most edtech UIs are cognitive noise for the very users they claim to serve.

The consequence: Sarah's 5–7 hours of weekly paperwork, multiplied by roughly 450,000 special education teachers serving 1.4 million autistic students in US public schools, is a systemic design failure that shows up in teacher burnout (40% turnover, versus 16% in general ed) and in the 50% gap in progress-data access reported by parents of children with disabilities.

ClassLens closes the evidence-to-insight gap. Photo in → structured trial data → goal mapping → trend analysis → teacher-ready materials, all on top of a single multimodal model.

---

## 3. What we built

A four-agent pipeline, each agent responsible for one well-defined transformation, each driven by Gemma 4 through native function calling:

**Agent 1 — Vision Reader.** Gemma 4 multimodal: a photo of student work in, a structured JSON transcription out, with observations a teacher actually needs (letter formation, engagement, time-on-task, sensory indicators) that OCR throws away.

**Agent 2 — IEP Mapper.** Function calling: the transcription is matched against that specific student's IEP goals, with confidence scores and an explicit alignment type (direct evidence, supporting evidence, prerequisite). No free-text hallucinations — every match is a schema-enforced function call.

**Agent 3 — Progress Analyst.** Thinking mode: 4–8 weeks of mapped evidence per goal is analyzed for trend, velocity, and projected mastery date, with explicit reasoning about confidence intervals. Trends become alerts (green/yellow/red) with recommendations.

**Agent 4 — Material Forge.** Function calling + thinking: generates seven material types across three audiences — teacher lesson plans, social stories, tracking sheets; parent progress letters, visual schedules, first-then boards; administrator data reports. Interests, sensory profile, and communication level are woven into every material. Everything is multilingual (EN/ES default, extensible).

One worked example of what the IEP Mapper produces for a real photo of Maya's (Grade 3, Level 2, dinosaur-obsessed) handwriting sample:

```json
{
  "evidence_id": "maya-2026-04-03",
  "mappings": [
    {
      "goal": "2.1_Written_Expression",
      "confidence": 0.92,
      "alignment": "direct_evidence",
      "observations": "Complete subject (dinosaur) and verb (is); capitalization inconsistent with convention"
    },
    {
      "goal": "3.4_Color_Identification",
      "confidence": 0.87,
      "alignment": "supporting_evidence",
      "observations": "Used 'green' spontaneously in context"
    }
  ]
}
```

That JSON is the entire audit trail for a moment of learning. Sarah used to type it herself. Now it writes itself while she's still with the student.

The full application ships as:

- **Next.js 16 + FastAPI** three-column teacher interface (student sidebar, content area, chat panel), with a dedicated print stylesheet for clean letter-size output of every material
- **7 student profiles** covering the core demographic range (verbal, non-verbal with AAC, cognitively unimpaired with sensory/pragmatic needs, across K–6), with 20 real work artifacts and precomputed pipeline outputs — the demo never waits on the API
- **165 tests** passing, 0 TypeScript errors, browser-path smoke test via Playwright against the real Next.js frontend
- **FERPA-aware by design**: synthetic student IDs, path-traversal validation on every router, sanitized model output, no secrets in the repo, no student audio or image ever sent to a non-Google provider

---

## 4. Why Gemma 4 specifically

Three capabilities of Gemma 4 are load-bearing in ClassLens. Any one missing, the project doesn't work.

**Multimodal vision.** Student work is visual. Handwriting, drawings, AAC screens, worksheets, behavior plot charts. A pre-Gemma-4 pipeline would need OCR plus vision-to-text plus layout parsing — three failure modes. Gemma 4 takes the photo directly and reasons about it with the teacher context already loaded. The observations it produces — "letter formation consistent with emerging proprioceptive control," "word spacing improved over last week's sample" — are pedagogical, not visual. OCR cannot do that. Proprietary vision models can do some of it, but Gemma 4 is the open model that both performs at this level **and** can run in a classroom without sending student work to a third party (see ADR-011 for the V2 on-device path via LiteRT-LM and AI Edge Eloquent).

**Function calling.** Every agent's output is a schema-enforced function call. Confidence scores are floats in [0, 1]. Alignment types are enums. Dates are ISO. The IEP Mapper cannot hallucinate a goal ID that doesn't exist in the student profile — it is a categorical function argument. This is the difference between an AI demo and an audit trail. When Sarah approves a generated lesson plan, the plan, the evidence it was built on, the goals it targets, and the trend it responds to are all traceable JSON, not prose that has to be re-parsed.

**Thinking mode.** The Progress Analyst detects trends on 4–8 weekly data points. That is a deeply noisy signal. Thinking mode lets Gemma 4 reason explicitly about statistical confidence — and decide, for example, that three consecutive flat scores are *not yet* a plateau alert, but five are. The Material Forge uses thinking mode to decide *why* a student whose communication is scaffolded with AAC needs a specific visual schedule shape, not just the default template. Thinking mode is the difference between a tool a teacher doubts and a tool she trusts.

Only one vendor in 2026 ships an open foundation model with all three capabilities, at a zero-cost free tier appropriate for a district that spent its budget on paraprofessionals. That vendor is Google. That model is Gemma 4.

---

## 5. Engineering decisions we're proud of

Eleven Architecture Decision Records are tracked in `docs/ADR.md`. The ones that actually moved judge-visible quality:

| ADR | Decision | Why it matters to a judge |
|---|---|---|
| ADR-001 | Gemma 4 via Google AI Studio (free tier) | Zero infrastructure cost; reproducible by any judge with an API key |
| ADR-002 | Four discrete agents, not one monolithic prompt | Each agent is independently testable; failure modes are isolated |
| ADR-003 | Pre-baked demo mode with precomputed caches | The 15 RPM free-tier limit never degrades the live demo |
| ADR-006 | Dual-track: Google AI Studio + Ollama edge | On-prem story for FERPA-sensitive districts; no vendor lock-in |
| ADR-008 | Three-tier fallback on every agent | Graceful degradation; no demo-day whiteboard failure |
| **ADR-011** | **Text-first voice capture in V1; Gemma 4 E4B on-device ASR in V2** | **Keeps V1 critical path 100% Gemma 4; V2 ships on LiteRT-LM once Windows Python bindings land** |

ADR-011 is worth expanding because it was written in the last sprint after a live spike:

- We built voice observation capture expecting `gemma-4-31b-it` to accept audio input.
- Google AI Studio turned out to gate audio off at the hosting layer on every Gemma variant, including the 3n E-series that has ASR built into the weights.
- We evaluated a Gemini transcription shim, Vertex AI for Gemma 3n, and on-device Gemma 4 E4B via the LiteRT-LM framework that powers Google's own AI Edge Eloquent dictation app.
- The spike confirmed LiteRT-LM Python bindings are Linux/macOS only with Windows "upcoming." We're on Windows.
- **Decision: ship text-first observation capture in V1, keep the critical path 100% Gemma 4, and put on-device Gemma 4 E4B ASR on the V2 roadmap.** The "Quick Observation" typed input is what teachers actually do anyway.

That entire decision is documented at `docs/plans/2026-04-12-audio-shim-decision.md`. It is the kind of engineering judgment a hackathon submission usually hides. We are putting it in front because it is the honest story and because it demonstrates that our Gemma 4 commitment survives contact with real infrastructure.

We also deliberately **did not use LangChain, LangGraph, or CrewAI.** Direct Gemma 4 calls through Pydantic-validated function schemas. Every API call is logged. Every state transition is explicit. Every piece of evidence has a traceable lineage from photo to generated material. In an education product where FERPA compliance is non-negotiable and teachers need to explain AI decisions to parents and administrators, framework abstractions are a liability, not an asset.

---

## 6. The three demo students

Every feature in ClassLens was trialed against three student archetypes that together span the real autism spectrum teachers see:

**Maya — Grade 3, Level 2, verbal.** Dinosaur-obsessed, 2nd-grade reading level, writes with support, inconsistent capitalization. *ClassLens impact:* Vision Reader produces structured trial data from her writing in 2 minutes instead of Sarah's prior 45; Material Forge generates a dinosaur-themed lesson plan that is actually pedagogically tight, not just thematically decorated. Observed outcome in pilot: **three extra guided-writing sessions per week** where previously there was time for one.

**Jaylen — Grade 1, Level 3, non-verbal, AAC-dependent.** Obsessed with trains, distressed by unexpected transitions. *ClassLens impact:* Visual schedules and first-then boards generated from his actual preferences and communication level, in 30 seconds instead of 20 minutes per schedule. Observed outcome: **reduced transition-related escalations** because the schedule is ready when Monday begins, not drafted in the moment.

**Sofia — Grade 5, Level 1, academically at/above grade.** Articulate, socially anxious, writes beautifully but struggles with organization. *ClassLens impact:* Progress Analyst surfaces that her written-organization goal and her peer-interaction goal are *connected* — small-group writing is the intervention both trends point to. Observed outcome: **Sofia's coordinated intervention plan** now comes out of the data instead of out of Sarah's gut.

Four additional students (Amara, Ethan, Lily, Marcus) round out the demo set with specific alert scenarios — Amara's 5-week social-skills decline, Ethan's 4-session handwriting plateau — so judges can see the Progress Analyst earn its keep on real trajectories, not hypotheticals.

---

## 7. Scale and what this adds up to

Sarah's 5–7 weekly hours, projected:

- **Small rural district** (200 students, 8 with ASD): ~8 × 5 = 40 hours/week reclaimed district-wide — one full-time staff equivalent.
- **Mid-size suburban district** (1,200 students, 45 with ASD): ~225 hours/week reclaimed — 5.6 FTE.
- **Large urban district** (5,000 students, 180 with ASD): ~900 hours/week reclaimed — 22 FTE.

These are time-reclamation estimates, not cost-reduction promises. The hours don't become a staffing cut; they become direct instructional minutes with students who are federally entitled to them. At a 60% adoption rate across US public-school districts over five years, the order-of-magnitude total is hundreds of millions of teacher-hours per year returned to instruction. We are being deliberately imprecise about a dollar figure because anyone can extrapolate one; only Sarah can tell you whether the Friday afternoon actually changed.

The equity case is concrete and narrower than "AI for good":

- **Parents with lower English literacy** get multilingual, visual progress letters instead of untranslated paper. ClassLens defaults to EN/ES and is extensible to every language Gemma 4 reads.
- **Rural districts with no specialist support** get trend analysis and intervention recommendations that normally live in a three-day conference the district can't afford to send a teacher to.
- **Non-verbal students** get evidence captured visually — drawing, AAC screens, behavior photos — in a system that treats visual communication as first-class data, not as a typed summary.

---

## 8. What we did not build, and why

This is a hackathon, not a product. We were disciplined about scope:

- **No student account system.** Synthetic IDs only. A production deployment would plug into the district's SIS (Skyward, Infinite Campus, PowerSchool). That integration is not a Gemma 4 problem.
- **No multi-tenant backend.** Single-district, single-classroom model. A district rollout needs row-level security, role-based access, and audit logging beyond what a demo should carry.
- **No automated parent-portal delivery.** Every generated material passes through a teacher approval step. "Nothing auto-sends" is an explicit product rule, not a TODO.
- **No Spanish training data curation.** Gemma 4's multilingual capability is what makes EN/ES work. We did not collect or label a dataset.
- **No live voice capture in V1.** ADR-011 above — on-device Gemma 4 E4B via LiteRT-LM is the V2 path.
- **No real IEP system integration.** Every student profile and IEP goal is synthetic but structurally accurate (modeled with a 15-year special ed teacher's oversight).

Each of these decisions is a scope call. A tool designed for Sarah's classroom is not the same tool as a district-wide procurement. We built the former well and documented the path to the latter.

---

## 9. How to try it

- **Live demo:** *[URL posted in submission form once the release gate opens]*
- **Source code:** *[GitHub link in submission form]*
- **Run locally:** `pip install -r requirements.txt` → `cd frontend && npm install` → `python -m uvicorn backend.main:app --port 8001` + `cd frontend && npm run dev`. Set `MODEL_PROVIDER=google` and `GOOGLE_AI_STUDIO_KEY=...` in `.env`.
- **Test suite:** `python -m pytest tests/ -q` (165 tests, ~5 min on CPU)
- **Browser smoke test:** `python scripts/browser_smoke.py` (Playwright, drives the real frontend)

**The team.**
**Sarah** — 15-year special education veteran, rural Idaho K-5 classroom, Carol Gray social story framework, autism-specific evidence-based intervention design. Built every student profile, reviewed every output type, provided the pilot classroom against which every feature was tested.
**Jeff** — VP of AI Engineering, full-stack developer, Sarah's husband. Wrote every line of code. Spent the last two years watching the problem before building the tool.

**The rule we held to.** Nothing in ClassLens auto-sends, auto-grades, or auto-decides. Every AI output goes in front of a teacher before it reaches a student, a parent, or a file. "Teacher-in-the-loop" is how a tool earns the trust of a classroom. We built for trust first, time second, and everything else after that.
