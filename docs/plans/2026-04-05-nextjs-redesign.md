# ClassLens ASD — Next.js + FastAPI Redesign

**Date:** 2026-04-05
**Goal:** Replace Streamlit UI with Next.js frontend + FastAPI backend. Make Gemma 4 the visible expert assistant throughout. Professional output rendering. Scale to dozens of students.

---

## 1. Architecture

**Framework:** Next.js 14 (App Router) + FastAPI backend + Tailwind CSS

**Why this stack:**
- Next.js gives real layout control, responsive design, deploys free on Vercel
- FastAPI wraps existing Python agent code with zero rewrite — 4 agents, pipeline, state store stay as-is
- Chat interface needs streaming support — FastAPI handles SSE natively, Next.js renders cleanly
- Long-term open source: React (most common frontend skill) + Python (most common AI/ML skill)

**Model access:** OpenRouter initially (single API key, routes to Gemma 4), with config option for Google AI Studio direct or Ollama local.

---

## 2. Three-Column Layout

| Column | Width | Content | Behavior |
|--------|-------|---------|----------|
| Left sidebar | ~240px | Student roster grouped by alerts then alphabetical. "+ Add Student" at bottom. | Always visible. Collapsible on mobile. |
| Center content | Flex | Scrollable student page OR class dashboard | Changes when you click a student |
| Right panel | ~320px | ClassLens Assistant (Gemma 4 chat). Context-aware. | Always visible. Prominent. Collapsible on mobile. |

**Routing — just 3 pages:**
- `/` — Class dashboard (before selecting a student)
- `/student/[id]` — Student detail page
- No other pages. Everything else happens in chat or inline.

---

## 3. UX Mental Model

**Student-anchored with smart alerts.** The student is always the anchor (how teachers think). Gemma 4 surfaces what needs attention proactively.

**Gemma 4 as expert IEP co-teacher** — not a generic chatbot. Speaks like an experienced special ed colleague. Uses teacher vocabulary. Never uses AI/ML jargon. Proactive but not pushy. Always defers to teacher judgment.

---

## 4. Class Dashboard (Home Screen)

What the teacher sees before clicking any student:

- **Greeting:** "Good morning, Sarah. You have 12 students, 34 active goals, 8 sessions this week."
- **Needs Attention section:** Gemma-generated alerts with action buttons
  - Plateau/regression alerts with [View] [Ask Assistant]
  - IEP review due dates with [Prepare Meeting Summary]
  - Parent messages with [Draft Reply]
- **Recent Activity timeline:** Chronological list of scans, materials generated, letters sent
- **No charts on this page.** Charts live on individual student pages. Dashboard is about "what needs attention" and "what happened recently."

Chat panel on dashboard is proactive — opens with relevant suggestions based on alerts.

---

## 5. Student Detail Page (Center Content)

Single scrollable page per student, ordered by teacher priority:

1. **Student header** — Name, grade, level badge, interests, communication style. Compact, always visible.
2. **Alerts banner** — Only if Gemma detected something. Dismissable. Inline action buttons.
3. **IEP Goals** — Cards: goal text, current %, trend arrow, last session. Click to expand: trial history chart, recent sessions, quick actions.
4. **Recent Work** — Timeline of scanned documents with thumbnails. Shows extraction results and goal mappings.
5. **Materials Library** — All generated materials for this student. Filterable by type. Shows draft/approved status.
6. **Quick Actions footer** — Sticky bar: "Scan Work" / "Generate Material" / "Write Parent Note"

---

## 6. Add Student Flow (Gemma 4 Showcase)

Conversational onboarding driven by the chat panel. Three Gemma capabilities in one flow:

1. Teacher clicks "+ Add Student"
2. Chat asks name and grade
3. Teacher uploads IEP document (PDF or photo)
4. **Gemma 4 multimodal** reads the document, extracts goals and accommodations via **function calling**
5. Chat presents extracted goals for teacher to confirm/edit
6. Chat asks clarifying questions: interests, communication style, sensory profile
7. Profile is built. Student appears in sidebar immediately.
8. Chat offers to generate first materials.

Center content area shows the profile building in real-time as each piece is confirmed.

**Competition value:** Judges see multimodal document reading, structured extraction, conversational reasoning, and domain expertise in one interaction.

---

## 7. Scan Work Flow (Conversational Capture)

Teacher drops an image into chat or clicks "Scan Work":

1. Gemma 4 multimodal reads the student work
2. **Instead of JSON dump:** Gemma explains what it sees in teacher language — "7/10 correct, all 3 errors involved regrouping"
3. Automatic trend context — "This is up from 60% last week"
4. Goal mapping explained — "This maps to Goal G2"
5. Suggested next actions — "Want me to generate a lesson plan? Look deeper at the trend?"
6. Teacher can request multiple outputs in one conversation turn
7. Edit loop is conversational — "take out the regrouping part" not form fields

**Competition value:** 4 Gemma capabilities (vision, function calling, reasoning, generation) in one natural interaction.

---

## 8. Chat Assistant — Tools and Personality

**System prompt personality:**
- Experienced special ed colleague, not a robot
- Concrete teacher vocabulary: "trial data," "prompting level," "present levels"
- No AI/ML jargon: no "tokens," "inference," "confidence scores"
- Proactive but deferential: "Here's what I see — what do you think?"

**Gemma 4 function calling tools available to assistant:**

```
get_student_profile(student_id)
scan_work_artifact(student_id, image)
analyze_goal_progress(student_id, goal_id)
generate_material(student_id, goal_id, type)
extract_iep_document(file)
create_student_profile(profile_data)
draft_parent_communication(student_id)
prepare_iep_meeting(student_id)
get_alerts()
```

The chat endpoint has access to all API capabilities via function calling — the assistant can do anything the UI buttons can do, through conversation.

---

## 9. Professional Output Rendering

Every generated material gets a purpose-built React component that renders it as a professional document. Same JSON data, transformed presentation.

**Design principles:**
- Every output looks like it came from a real school system
- Teacher can print, email, or present in IEP meeting without editing
- ClassLens header, student info, date on every output
- Footer: "Generated by ClassLens ASD · Teacher review required"

**Output types:**

### Lesson Plan
- Single page, printable
- Student name, goal, date header
- Interest-themed title (e.g., "Minecraft Block Regrouping")
- Sections: Objective, Warm-up, Main Activity, Materials Needed, Scaffolding Notes
- Materials checklist with checkboxes
- Sensory/accommodation notes at bottom

### Parent Communication
- Email-ready format, warm tone, no jargon
- Greeting, highlights with emoji markers, "Try at Home" section
- Teacher signature line
- School branding footer

### Admin/IEP Report
- Multi-page, meeting-ready
- "Confidential — IEP Team Use Only" header
- Executive summary paragraph
- Goal-by-goal analysis with embedded progress charts
- Present level, target, recommendation per goal
- Accommodations & notes section
- Teacher signature line

### Social Story
- Carol Gray format, picture-book layout
- One page per scene with illustration placeholder
- Student's interest theme throughout
- Sentence type labels (descriptive, perspective, directive)
- AAC symbol integration for non-verbal students

### Tracking Sheet
- Printable data collection grid
- Goal text and measurement criteria at top
- Date/trial/result columns
- Space for teacher notes
- Target criterion highlighted

### Visual Schedule
- Sequential step cards with numbering
- Icon placeholder per step
- "First → Then" format option
- Checkbox for completion tracking

**Implementation:**
- React components per output type with proper layout
- Print CSS (`@media print`) for clean printing
- PDF export via browser `window.print()` or react-pdf
- Plotly charts render as static images for PDF/print

---

## 10. Visual Design System

**Core principle:** Calm, organized classroom — not a SaaS dashboard. Warm, predictable, never overwhelming.

### Colors
```
Background:     #FAFAFA  (warm off-white)
Surface/Cards:  #FFFFFF
Primary:        #4A7FA5  (calm blue)
Primary hover:  #3D6B8E
Text primary:   #2C3E50  (near-black, high contrast)
Text secondary: #6B7C8D
Success/Up:     #4ECDC4  (teal)
Warning:        #E8A838  (warm amber)
Danger/Down:    #D4726A  (soft red, not alarming)

ASD Level badges:
  Level 1: #4ECDC4 bg, #1A6B63 text
  Level 2: #5B8FB9 bg, #FFFFFF text
  Level 3: #8B7EC8 bg, #FFFFFF text
```

No pure red anywhere. High contrast ratios (WCAG AA). Cool blues dominate.

### Typography
```
Font:     Inter (clean, legible, free)
Headings: Inter 600, not bold (less visual pressure)
Body:     Inter 400, 15px (slightly larger — tired teacher eyes)
Captions: Inter 400, 13px, text-secondary
Chat:     Inter 400, 14px
```

No monospace anywhere in teacher UI. No JSON, no code visible.

### Spacing & Interaction
- 12px border radius on cards
- 16px padding minimum inside cards
- 24px gap between sections
- Max 3 levels of visual hierarchy per screen
- 800px max content width in center column
- Buttons: primary (filled blue), secondary (outlined), ghost (text)
- Loading: calm pulse animation, not spinners
- Transitions: 200ms ease-out
- No auto-dismiss toasts — inline confirmations only
- Every destructive action requires confirmation

### Chat Panel Styling
```
Background:     #F5F6F8 (slightly cooler than main bg)
Assistant msgs: White bubble, left-aligned
Teacher msgs:   Primary blue bubble, right-aligned, white text
Action cards:   White card, left border (teal=generated, amber=alert)
Approve/Edit:   Inline buttons below content
```

---

## 11. Data Model Changes

JSON file storage stays (no database needed for competition + early open source).

### New directory structure
```
data/
├── students/           (existing, unchanged)
├── documents/          (NEW — per-student folders)
│   └── {student_id}/
│       ├── {date}_{type}.jpg    (original image)
│       └── {date}_{type}.json   (extraction result)
├── materials/          (NEW — per-student folders)
│   └── {student_id}/
│       └── {type}_{goal}_{date}.json  (with status field)
├── alerts/
│   └── active_alerts.json
├── conversations/      (NEW — chat history)
│   └── {student_id}_{date}.json
└── precomputed/        (existing, unchanged)
```

### New/modified schemas

```python
# Added to StudentProfile
documents_count: int = 0
last_session_date: str | None
created_via: str = "manual"  # "manual" | "chat" | "iep_upload"

# New: Alert
class Alert(BaseModel):
    id: str
    student_id: str
    alert_type: str          # "plateau" | "regression" | "iep_review" | "parent_message"
    goal_id: str | None
    title: str
    detail: str
    suggested_action: str
    created_date: str
    dismissed: bool = False

# New: DocumentRecord
class DocumentRecord(BaseModel):
    id: str
    student_id: str
    filename: str
    doc_type: str            # "worksheet" | "iep_pdf" | "tally_sheet" | etc.
    upload_date: str
    extraction: dict
    mapped_goals: list[str]
    image_path: str
```

---

## 12. API Endpoints

Base URL: `http://localhost:8000/api`

### Student management
```
GET    /students              — List all (sidebar roster)
GET    /students/:id          — Full profile + goals + history
POST   /students              — Create (from chat-built profile)
PUT    /students/:id          — Update profile
DELETE /students/:id          — Remove student
```

### Document capture + pipeline
```
POST   /capture               — Upload image + run full pipeline
POST   /documents/upload      — Upload IEP PDF (Gemma extracts content)
GET    /students/:id/documents — List scanned documents
```

### Material generation
```
POST   /materials/generate    — Generate material for student + goal
GET    /students/:id/materials — List all generated materials
PUT    /materials/:id/approve  — Mark as approved
```

### Chat assistant
```
POST   /chat                  — Send message (streaming response)
                                Payload: message, student_id, conversation_history
```

### Alerts
```
GET    /alerts                — All active alerts
PUT    /alerts/:id/dismiss    — Dismiss alert
```

---

## 13. Competition Strategy

This redesign maximizes Gemma 4 visibility:

| Gemma 4 Capability | Where Judges See It |
|---------------------|---------------------|
| Multimodal vision | Scan worksheets, read IEP PDFs |
| Function calling | Structured extraction, goal mapping, material generation |
| Thinking mode | Progress analysis with visible reasoning |
| Text generation | Chat responses, parent letters, lesson plans, social stories |
| Conversational | Every interaction flows through the assistant |

**Demo script moments:**
1. Add Student via IEP upload (multimodal + function calling + conversation)
2. Scan worksheet with conversational follow-up (vision + reasoning)
3. Generate dinosaur lesson plan from conversation (generation + personalization)
4. Parent note edited conversationally (teacher-in-the-loop)
5. IEP meeting prep in 30 seconds (thinking mode + structured output)

**The assistant is always visible.** Judges watch Gemma 4 working throughout the entire demo, not hidden behind spinners.
