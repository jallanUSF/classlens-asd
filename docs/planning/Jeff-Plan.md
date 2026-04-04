# Jeff's Plan — ClassLens ASD
## The Tech Side of the Build

**Your role:** Architect, builder, competition strategist, video producer
**Deadline:** May 18, 2026 (submit May 17 for buffer)
**Dependency:** Sarah's student profiles (Week 1) unlock everything from Week 2 onward

---

## The Big Picture

You're building a four-agent pipeline on Gemma 4 and wrapping it in a demo app. The tech has to be real and functional, but remember: it only needs to be **demo-quality**, not production-quality. The video is 70% of the score. Every hour you spend over-engineering backend plumbing is an hour stolen from the demo and the story.

**Your guiding principle:** Build the shortest path to a compelling 3-minute video with a working live demo behind it.

---

## Architecture Recap

```
Photo of student work
    → Agent 1: Vision Reader (Gemma 4 multimodal OCR)
    → Agent 2: IEP Mapper (function calling → match to IEP goals)
    → Agent 3: Progress Analyst (thinking mode → trends, alerts, admin reports)
    → Agent 4: Material Forge (lesson plans, social stories, schedules,
                                tracking sheets, parent comms)
    → Teacher reviews and approves
```

### Material Forge Output Types (7 total)

Based on Sarah's input, Material Forge generates seven output types organized by audience:

**For the teacher (daily use):**
1. **Goal-aligned lesson plans & activities** — Given an IEP goal, generate scaffolded lesson ideas, activities, and practice tasks that build toward mastery. Incorporate student's interests. *(Sarah's #1 request — she asked for this twice.)*
2. **Printable data tracking sheets** — Per-goal clipboard-ready sheets for use during instruction. Not a screen — a physical tool she carries during the day.
3. **Social stories** (Carol Gray framework) — Sentence types, ratios, first person, student interests, vocabulary-matched.
4. **Visual schedule descriptions** — Concrete, sequential, para-actionable.
5. **First-Then board text** — Binary structure with student's reinforcers.

**For parents:**
6. **Parent communications** — References specific student work, celebrates a success, suggests one home activity. Warm but professional. Multilingual via Gemma 4.

**For administrators / IEP teams:**
7. **Admin progress reports** — Polished, professional reports with trend charts, goal summaries, and compliance-ready language. Generated from Progress Analyst data, formatted for non-teacher audiences who "eat up fancy reports and data."

Model: `gemma-4-26B-A4B-it` for all agents (MoE = fast, native function calling + thinking + multimodal). Edge demo with `gemma-4-E4B-it` via Ollama if pursuing Special Tech track.

State store: JSON files per student. No database.
Demo app: Streamlit or Gradio.
Deployment: Streamlit Community Cloud or HF Spaces (free, public URL).

---

## Weekly Execution Plan

### WEEK 1: Apr 5-11 — Environment + Proof of Concept

**Goal:** Can Gemma 4 read messy handwriting? If not, the whole project pivots.

- [ ] Set up Gemma 4 access on Kaggle Notebooks (free GPU)
- [ ] Install Ollama locally, pull gemma4, verify it runs
- [ ] Test multimodal vision on 3-5 sample handwritten images (use generic samples until Sarah's arrive)
- [ ] Benchmark OCR accuracy — if handwriting recognition is <70% accurate, assess fallbacks:
  - Cleaner printed worksheets with handwritten answers
  - Higher visual token budget (1120)
  - Prompt engineering for ambiguous characters
- [ ] Define all function calling JSON schemas (Vision Reader, IEP Mapper, Progress Analyst, Material Forge)
- [ ] Create student profile JSON template (pre-fill with Maya example from tech-playbook)
- [ ] Build `gemma_client.py` — thin wrapper for consistent API calls across all agents
- [ ] Set up GitHub repo with folder structure
- [ ] **Joint session with Sarah:** Have her walk you through IEP data collection process (record it or take detailed notes)

**Blocker check:** If Gemma 4 multimodal can't handle handwriting at all, pivot to:
- Typed/printed worksheets only (less impressive but still viable)
- Use the handwriting OCR as a "stretch goal" shown at the end of the video

**Sarah dependency:** Student profiles ideally arrive by end of Week 1. You can start with the Maya example from the tech-playbook, but real profiles make Week 2 much more productive.

---

### WEEK 2: Apr 12-18 — Agent 1: Vision Reader

**Goal:** Photo in → structured JSON out, validated by Sarah.

- [ ] Build `vision_reader.py` with Gemma 4 function calling
- [ ] Test on each work artifact type:
  - Handwritten math worksheets
  - Behavior tally sheets
  - Task-analysis checklists
  - Visual schedule photos
  - Free-response / short-answer
- [ ] Implement variable resolution strategy:
  - 1120 tokens for handwritten work
  - 560 tokens for printed + handwritten
  - 280 tokens for tally sheets / checklists
- [ ] Handle edge cases: partial completion, illegible writing, angled photos, shadows
- [ ] **Give Sarah 3-5 transcription outputs to review** — does the AI read what she reads?
- [ ] Iterate based on her feedback

**Key metric:** Sarah looks at the AI transcription and the original photo side-by-side and says "yes, that's what it says" for 80%+ of items.

---

### WEEK 3: Apr 19-25 — Agents 2-3: IEP Mapper + Progress Analyst

**Goal:** Transcribed work → mapped to IEP goals → trend analysis.

- [ ] Build `state_store.py` — read/write student JSON profiles
- [ ] Populate student profiles from Sarah's templates (convert her docs to JSON)
- [ ] Build `iep_mapper.py`:
  - Load student profile via `get_student_profile` function call
  - Match transcribed work to IEP goals via `map_work_to_goals`
  - Record trial data via `record_trial_data`
- [ ] Build `progress_analyst.py` with thinking mode (`<|think|>` token):
  - Trend detection: improving / on_track / plateaued / regressing
  - Progress note generation (IEP-ready language)
  - Regression alerts (conservative — only flag actionable things)
- [ ] Test end-to-end: image → transcription → goal mapping → trial data → trend analysis
- [ ] Simulate 4+ weeks of historical data for each student to test trend detection
- [ ] **Give Sarah mapped outputs to review:** "Would you agree this worksheet maps to Goal G2?"
- [ ] **Give Sarah progress notes to review:** "Would you submit this to the IEP team?"

---

### WEEK 4: Apr 26 - May 2 — Agent 4: Material Forge + Integration

**Goal:** Full pipeline works end-to-end. All 7 Material Forge output types functional.

- [ ] Build `material_forge.py` with all output types:
  - **Lesson plans & activities** (IEP goal → scaffolded lessons incorporating student interests) — PRIORITY, Sarah's #1 ask
  - **Printable data tracking sheets** (per-goal, clipboard-ready format — generate as HTML/PDF)
  - Social stories (Carol Gray framework — sentence types, ratios, first person, student interests)
  - Visual schedule descriptions (concrete, sequential, para-actionable)
  - First-Then board text (binary structure with student's reinforcers)
  - Parent communications (specific to today's work, warm tone, one home activity suggestion)
- [ ] Build `report_generator.py`:
  - **Admin progress reports** — polished PDF with trend charts, goal summaries, professional language
  - Uses Progress Analyst data as input, formatted for administrators/IEP teams
  - Include: student name, goal summaries, trend arrows, percentage charts, narrative notes
  - Design to impress: Sarah says "admin/managers eat up fancy reports and data"
- [ ] Wire all four agents into a single pipeline: `run_pipeline(student_id, image) → full_output`
- [ ] Test with each student profile
- [ ] **Give Sarah all material types to review** — lesson plans, tracking sheets, social stories, schedules, parent comms, admin report
- [ ] Start iteration based on her feedback
- [ ] Begin Streamlit app skeleton:
  - Upload screen (select student, upload photo)
  - Processing indicator (shows pipeline running)
  - Dashboard screen (IEP goals with trend arrows)
  - Outputs screen (generated materials with approve/edit/regenerate)
  - **Reports screen** (generate admin/IEP team progress report — print or export as PDF)
  - **Lesson Planner screen** (input IEP goal → get lesson ideas + tracking sheet)

---

### WEEK 5: May 3-9 — Demo App + Video Prep

**Goal:** Live demo deployed. Video content captured.

- [ ] Complete Streamlit app with all screens
- [ ] Add pre-loaded sample data so judges can try it immediately (no setup)
- [ ] Deploy to Streamlit Community Cloud or HF Spaces — verify public URL works
- [ ] Test Ollama local deployment for Special Tech track (if pursuing)
- [ ] Full end-to-end testing: upload 5+ artifacts across all students, verify all outputs
- [ ] **Sarah's final material review** — lesson plans, tracking sheets, social stories, schedules, parent comms, admin reports all approved
- [ ] Capture screen recordings of the demo running (for video B-roll)
- [ ] Draft video storyboard (see tech-playbook Section 4.2 for the template)
- [ ] Coordinate Sarah's video recording — she can record her segments independently on phone
- [ ] Create cover image for Kaggle media gallery

---

### WEEK 6: May 10-17 — Video + Writeup + Submit

**Goal:** Everything submitted to Kaggle by May 17.

- [ ] Write Kaggle writeup (≤1,500 words) — first draft by May 11
  - Structure: Hook (100w) → Solution (200w) → Architecture (400w) → ASD Design (300w) → Demo Walkthrough (300w) → Impact (200w)
- [ ] Sarah reviews writeup for ASD/teacher accuracy
- [ ] Record Jeff's voiceover segments for video (architecture explanation, tech credibility)
- [ ] Edit video (≤3 minutes) — combine Sarah's phone clips + screen recordings + VO
  - iMovie or CapCut is fine. Authenticity > polish.
- [ ] Upload video to YouTube (public or unlisted)
- [ ] Final testing of live demo URL
- [ ] Assemble Kaggle submission:
  - [ ] Writeup with track selected (Future of Education)
  - [ ] Video link attached
  - [ ] GitHub repo link attached
  - [ ] Live demo URL attached
  - [ ] Cover image in media gallery
- [ ] **Submit by May 17** (one day buffer before May 18 deadline)
- [ ] Verify submission is marked "Submitted" not "Draft"

---

## Risk Register

| Risk | Severity | Mitigation | Decision Point |
|------|----------|------------|----------------|
| Gemma 4 can't read messy handwriting | HIGH | Test Week 1. Fallback: cleaner printed worksheets. Higher token budget. | End of Week 1 |
| Sarah's profiles arrive late | MEDIUM | Start with Maya example. Real profiles make Week 2-3 better but aren't blocking for Week 1. | Mid-Week 1 |
| Function calling unreliable | MEDIUM | Gemma 4 has native support. Fallback: structured JSON output parsing. | Week 2 |
| Can't deploy live demo with GPU | MEDIUM | Use Google AI Studio API as backend, or pre-recorded demo. Kaggle Notebooks count as code demo. | Week 5 |
| Video recording logistics | LOW | Sarah records independently on phone. Doesn't need same session as screen recording. | Week 5 |
| Writeup exceeds 1,500 words | LOW | Technical details go in code comments. Writeup is for story + architecture overview only. | Week 6 |

---

## Multi-Track Prize Strategy

| Track | Prize | Action Required |
|-------|-------|-----------------|
| **Future of Education** (primary) | $10K | Already aligned — multi-tool agents + individual adaptation + educator empowerment. Lesson plan generation + admin reports strengthen "seamless integration" angle. |
| **Main Track** | $50K-$10K | Strong video + real impact. Multi-stakeholder story (teacher + student + admin) elevates impact score. |
| **Digital Equity & Inclusivity** | $10K | Emphasize ASD = inclusivity in writeup. No extra tech work. |
| **Ollama Special Tech** | $10K | Demo Gemma 4 E4B running locally. Privacy story (student data never leaves school). ~2 hours of work in Week 5. |

**Max possible: $70K** (Main 1st + Education + Ollama). Realistic target: Education + one other.

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| Apr 4 | Gemma 4 26B-A4B-it as primary model | MoE efficiency (only 4B active params) + native function calling + multimodal + thinking mode |
| Apr 4 | Streamlit over Gradio for demo | Simpler deployment, free cloud hosting, cleaner UI for non-technical judges |
| Apr 4 | JSON files over database | Hackathon scope — no persistence complexity needed |
| Apr 4 | No LangChain/LangGraph | Cleaner code for judges to read, fewer dependencies, shows direct Gemma 4 usage |
| Apr 4 | Expanded Material Forge to 7 output types | Sarah's input: lesson plans are her #1 ask (said it twice). Admin reports serve second audience (administrators). Data tracking sheets = physical classroom tool. |
| Apr 4 | Added admin/IEP team as second audience | Sarah: "Admin/managers eat up fancy reports and data." Multi-stakeholder impact strengthens competition story. |
| | | |
