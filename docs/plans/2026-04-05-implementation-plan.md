# Next.js + FastAPI Redesign — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace Streamlit UI with a Next.js frontend + FastAPI backend. Gemma 4 as a visible conversational assistant throughout. Professional output rendering. Scale to dozens of students.

**Architecture:** Three-column layout (student sidebar, content area, chat panel). FastAPI wraps existing Python agents — no rewrite. Next.js App Router with Tailwind + shadcn/ui for the frontend. OpenRouter for model access initially.

**Tech Stack:** Next.js 14 (App Router), FastAPI, Tailwind CSS, shadcn/ui, Python 3.11+, OpenRouter API, Plotly (charts), react-pdf (print)

**Design doc:** `docs/plans/2026-04-05-nextjs-redesign.md`

---

## Sprint 1: FastAPI Backend (Days 1-3)

### Task 1: Project scaffolding and dependencies

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/.env.example`

**Step 1: Create backend directory and requirements**

```
backend/
├── main.py
├── requirements.txt
├── .env.example
├── routers/
│   ├── __init__.py
│   ├── students.py
│   ├── capture.py
│   ├── materials.py
│   ├── chat.py
│   └── alerts.py
└── services/
    ├── __init__.py
    └── chat_service.py
```

`backend/requirements.txt`:
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
python-multipart>=0.0.18
python-dotenv>=1.0.0
google-genai>=1.0.0
pydantic>=2.10.0
Pillow>=10.0.0
plotly>=5.24.0
jinja2>=3.1.0
sse-starlette>=2.0.0
httpx>=0.28.0
```

`backend/.env.example`:
```
OPENROUTER_API_KEY=your_key_here
GOOGLE_AI_STUDIO_KEY=optional_direct_key
MODEL_PROVIDER=openrouter
MODEL_NAME=google/gemma-4-27b-it
```

**Step 2: Create FastAPI entry point**

`backend/main.py` — CORS-enabled FastAPI app that imports routers. Mounts existing `data/` directory. Includes health check endpoint.

**Step 3: Verify server starts**

Run: `cd backend && uvicorn main:app --reload --port 8000`
Expected: Server starts, `GET /health` returns `{"status": "ok"}`

**Step 4: Commit**

```bash
git add backend/
git commit -m "feat: scaffold FastAPI backend with router structure"
```

---

### Task 2: Student CRUD endpoints

**Files:**
- Create: `backend/routers/students.py`
- Reuse: `core/state_store.py` (import directly, no copy)

**Step 1: Write the test**

Create `backend/tests/test_students_api.py`:
```python
from fastapi.testclient import TestClient

def test_list_students(client):
    resp = client.get("/api/students")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # maya, jaylen, sofia

def test_get_student(client):
    resp = client.get("/api/students/maya_2026")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Maya Chen"
    assert "iep_goals" in data

def test_get_student_not_found(client):
    resp = client.get("/api/students/nonexistent")
    assert resp.status_code == 404

def test_create_student(client):
    new_student = {
        "student_id": "test_student",
        "name": "Test Student",
        "grade": 3,
        "asd_level": 2,
        "communication_level": "verbal",
        "interests": ["coding"],
        "iep_goals": []
    }
    resp = client.post("/api/students", json=new_student)
    assert resp.status_code == 201

def test_delete_student(client):
    resp = client.delete("/api/students/test_student")
    assert resp.status_code == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_students_api.py -v`
Expected: FAIL — router not implemented

**Step 3: Implement students router**

`backend/routers/students.py`:
- `GET /api/students` — reads all JSON files from `data/students/`, returns list of profile summaries
- `GET /api/students/{student_id}` — reads single JSON file, returns full profile
- `POST /api/students` — writes new JSON file to `data/students/`
- `PUT /api/students/{student_id}` — updates existing JSON file
- `DELETE /api/students/{student_id}` — removes JSON file

Key: These endpoints read/write the same `data/students/*.json` files the existing agents use. No new data layer.

**Step 4: Run tests, verify pass**

Run: `pytest backend/tests/test_students_api.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add backend/routers/students.py backend/tests/
git commit -m "feat: student CRUD API endpoints"
```

---

### Task 3: Capture endpoint (pipeline integration)

**Files:**
- Create: `backend/routers/capture.py`
- Reuse: `core/pipeline.py`, `agents/*`, `tests/mock_api_responses.py`

**Step 1: Write the test**

```python
def test_capture_sample_image(client):
    """Upload a sample image and run pipeline."""
    with open("data/sample_work/maya_math_worksheet.png", "rb") as f:
        resp = client.post(
            "/api/capture",
            data={"student_id": "maya_2026", "work_type": "worksheet", "subject": "math"},
            files={"image": ("maya_math.png", f, "image/png")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "transcription" in data
    assert "goal_mapping" in data
```

**Step 2: Implement capture router**

`backend/routers/capture.py`:
- `POST /api/capture` — accepts multipart form (image file + student_id + work_type + subject)
- Saves uploaded image to `data/documents/{student_id}/`
- Runs `ClassLensPipeline.process_work_artifact()` (uses precomputed cache or live API)
- Returns pipeline result as JSON
- Also saves a `DocumentRecord` JSON alongside the image

**Step 3: Test and commit**

---

### Task 4: Materials generation endpoint

**Files:**
- Create: `backend/routers/materials.py`
- Reuse: `agents/material_forge.py`

**Step 1: Implement materials router**

- `POST /api/materials/generate` — accepts `{student_id, goal_id, material_type}`
- Calls `MaterialForge.generate_*()` methods
- Saves result to `data/materials/{student_id}/`
- Returns generated material JSON
- `GET /api/students/{student_id}/materials` — lists all saved materials
- `PUT /api/materials/{id}/approve` — updates status field

**Step 2: Test and commit**

---

### Task 5: Chat endpoint with streaming

**Files:**
- Create: `backend/routers/chat.py`
- Create: `backend/services/chat_service.py`

**Step 1: Implement chat service**

`backend/services/chat_service.py`:
- Builds system prompt with current student context (profile, goals, recent trials)
- Defines Gemma 4 function calling tools (get_profile, scan_work, generate_material, etc.)
- Sends message to model via OpenRouter API (or Google AI Studio, or Ollama — configurable)
- Streams response back via Server-Sent Events (SSE)
- When Gemma calls a function tool, executes it against the real backend services and returns result to model for continued generation

**Step 2: Implement chat router**

`backend/routers/chat.py`:
- `POST /api/chat` — accepts `{message, student_id, conversation_history}`
- Returns SSE stream of assistant response chunks
- Handles function call execution inline

**Step 3: Test with curl**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Maya", "student_id": "maya_2026", "conversation_history": []}'
```

Expected: Streaming response about Maya's profile and goals.

**Step 4: Commit**

---

### Task 6: Alerts endpoint

**Files:**
- Create: `backend/routers/alerts.py`

**Step 1: Implement alerts router**

- `GET /api/alerts` — scans all students, identifies plateaus/regressions/upcoming reviews
- `PUT /api/alerts/{id}/dismiss` — marks alert as dismissed
- Alert generation logic: analyze last N trial sessions per goal, flag plateaus (3+ sessions within 5% range), regressions (downward trend), IEP reviews (date-based)

**Step 2: Commit**

---

### Task 7: Document upload endpoint (IEP PDF extraction)

**Files:**
- Create: `backend/routers/documents.py`

**Step 1: Implement documents router**

- `POST /api/documents/upload` — accepts PDF/image + student_id
- Sends to Gemma 4 multimodal for extraction (goals, accommodations, present levels)
- Returns structured extraction result
- `GET /api/students/{student_id}/documents` — lists all uploaded documents

**Step 2: Commit**

---

## Sprint 2: Next.js Frontend — Layout & Shell (Days 4-6)

### Task 8: Next.js project scaffolding

**Files:**
- Create: `frontend/` directory via `create-next-app`

**Step 1: Scaffold project**

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --no-eslint
cd frontend
npx shadcn@latest init
```

**Step 2: Install additional dependencies**

```bash
npm install @ai-sdk/react  # for chat streaming UI
npm install plotly.js react-plotly.js  # charts
npm install lucide-react  # icons
```

**Step 3: Configure API proxy**

`frontend/next.config.js` — proxy `/api/*` to `http://localhost:8000/api/*` in dev.

**Step 4: Commit**

---

### Task 9: Three-column layout shell

**Files:**
- Create: `frontend/src/app/layout.tsx` (modify default)
- Create: `frontend/src/components/sidebar/StudentSidebar.tsx`
- Create: `frontend/src/components/chat/ChatPanel.tsx`
- Create: `frontend/src/app/page.tsx` (dashboard)

**Step 1: Implement layout**

Root layout with three columns:
- Left: `<StudentSidebar />` — 240px, lists students from `GET /api/students`
- Center: `{children}` — flex content area
- Right: `<ChatPanel />` — 320px, chat interface stub

**Step 2: Implement StudentSidebar**

- Fetches `/api/students` on mount
- Groups by alerts (needs attention first, then alphabetical)
- Each student: emoji + name + grade + level badge
- "+ Add Student" button at bottom
- Click navigates to `/student/[id]`
- Highlights active student

**Step 3: Implement ChatPanel stub**

- Message list (scrollable)
- Text input at bottom
- "ClassLens Assistant" header
- Hardcoded welcome message for now
- Streaming integration comes in Sprint 3

**Step 4: Implement dashboard page (center)**

- Greeting: "Good morning! You have N students, N goals, N sessions"
- Needs Attention section: fetches `/api/alerts`
- Recent Activity timeline: fetches from student documents

**Step 5: Commit**

---

### Task 10: Design system — Tailwind config + global styles

**Files:**
- Modify: `frontend/tailwind.config.ts`
- Create: `frontend/src/styles/design-tokens.css`

**Step 1: Configure Tailwind with our color palette**

```
primary: #4A7FA5, success: #4ECDC4, warning: #E8A838, danger: #D4726A
bg: #FAFAFA, surface: #FFFFFF, text: #2C3E50, text-muted: #6B7C8D
Level badges: L1 teal, L2 blue, L3 purple
```

Font: Inter, border-radius: 12px default, spacing scale per design doc.

**Step 2: Commit**

---

## Sprint 3: Student Detail Page + Chat Integration (Days 7-10)

### Task 11: Student detail page — header + goals

**Files:**
- Create: `frontend/src/app/student/[id]/page.tsx`
- Create: `frontend/src/components/student/StudentHeader.tsx`
- Create: `frontend/src/components/student/GoalCard.tsx`
- Create: `frontend/src/components/student/AlertBanner.tsx`

**Step 1: Student page fetches profile**

`/student/[id]/page.tsx` — server component, fetches `GET /api/students/{id}`.
Renders: StudentHeader → AlertBanner → GoalCards → RecentWork → Materials → QuickActions.

**Step 2: Implement GoalCard**

- Goal title, domain, current %, trend arrow
- Expandable: trial history mini-chart (Plotly), last 3 sessions, quick action buttons
- Click "Scan Work for This Goal" → opens chat with context

**Step 3: Implement AlertBanner**

- Only renders if student has active alerts
- Amber background, dismissable
- Action buttons inline: "Generate Materials" / "Ask Assistant"

**Step 4: Commit**

---

### Task 12: Student detail page — recent work + materials

**Files:**
- Create: `frontend/src/components/student/RecentWork.tsx`
- Create: `frontend/src/components/student/MaterialsLibrary.tsx`
- Create: `frontend/src/components/student/QuickActions.tsx`

**Step 1: RecentWork component**

- Fetches `GET /api/students/{id}/documents`
- Timeline view: thumbnail + date + "7/10, mapped to G2" summary
- Click to expand extraction details

**Step 2: MaterialsLibrary component**

- Fetches `GET /api/students/{id}/materials`
- Filterable by type (lesson plan, social story, etc.)
- Each shows status badge (draft/approved)
- Click to view full rendered material

**Step 3: QuickActions sticky footer**

- Three buttons: "Scan Work" / "Generate Material" / "Write Parent Note"
- Each triggers the chat panel with pre-filled context

**Step 4: Commit**

---

### Task 13: Chat panel — full streaming integration

**Files:**
- Modify: `frontend/src/components/chat/ChatPanel.tsx`
- Create: `frontend/src/components/chat/ChatMessage.tsx`
- Create: `frontend/src/components/chat/ActionCard.tsx`
- Create: `frontend/src/hooks/useChat.ts`

**Step 1: useChat hook**

- Manages conversation history in state
- Sends messages to `POST /api/chat` with current student_id
- Handles SSE streaming (reads response chunks, appends to current message)
- Detects action cards in response (material generated, profile built) and renders them inline

**Step 2: ChatMessage component**

- Assistant messages: white bubble, left-aligned, supports markdown rendering
- Teacher messages: blue bubble, right-aligned
- Action cards: white card with colored left border, embedded buttons (Approve/Edit/Regenerate)

**Step 3: Context awareness**

- When teacher navigates to a student page, chat receives context update
- Assistant greets with relevant info: "Looking at Maya — she has 2 alerts"
- When teacher clicks quick actions, chat pre-fills relevant prompt

**Step 4: Commit**

---

### Task 14: Add Student flow (chat-driven)

**Files:**
- Create: `frontend/src/app/student/new/page.tsx`
- Modify: `backend/services/chat_service.py` (add student creation tools)

**Step 1: New student page**

- Minimal center content: "Let's set up a new student — the assistant will guide you."
- Real-time profile card builds as chat confirms each piece
- File drop zone for IEP PDF upload (sends to `/api/documents/upload`)

**Step 2: Chat service — student creation tools**

- Add `extract_iep_document` and `create_student_profile` to Gemma function calling tools
- Chat service handles multi-turn conversation flow
- On profile completion, redirects to new student's page

**Step 3: Commit**

---

## Sprint 4: Professional Output Rendering (Days 11-13)

### Task 15: Lesson plan renderer

**Files:**
- Create: `frontend/src/components/materials/LessonPlanView.tsx`

**Step 1: Implement professional layout**

- ClassLens header + date
- Student name, goal, interest theme
- Sections: Objective, Warm-up, Main Activity, Materials (checkboxes), Scaffolding Notes
- Print CSS: `@media print` hides nav/chat, renders clean single-page document
- Approve/Edit/Regenerate buttons (hidden in print)

**Step 2: Commit**

---

### Task 16: Parent communication renderer

**Files:**
- Create: `frontend/src/components/materials/ParentLetterView.tsx`

- Email-ready format, warm tone
- Greeting, highlights with icons, "Try at Home" section
- Teacher signature line
- Print-friendly

---

### Task 17: Admin/IEP report renderer

**Files:**
- Create: `frontend/src/components/materials/AdminReportView.tsx`

- Multi-section: executive summary, goal-by-goal with embedded Plotly charts
- "Confidential" header
- Present level, target, recommendation per goal
- Static chart rendering for print
- Teacher signature line

---

### Task 18: Social story, tracking sheet, visual schedule renderers

**Files:**
- Create: `frontend/src/components/materials/SocialStoryView.tsx`
- Create: `frontend/src/components/materials/TrackingSheetView.tsx`
- Create: `frontend/src/components/materials/VisualScheduleView.tsx`

- Each gets a purpose-built layout per the design doc
- All include print CSS and approve/edit controls

**Step: Commit all renderers**

---

## Sprint 5: Polish + Deploy (Days 14-17)

### Task 19: Mobile responsive layout

- Sidebar collapses to hamburger menu on mobile
- Chat panel collapses to floating action button
- Center content goes full-width
- Quick actions bar sticks to bottom on mobile

### Task 20: OpenRouter integration

**Files:**
- Modify: `core/gemma_client.py` or create `backend/services/model_provider.py`

- OpenRouter uses OpenAI-compatible API format
- Config toggle: `MODEL_PROVIDER=openrouter|google|ollama`
- Single API key for OpenRouter, routes to Gemma 4

### Task 21: Vercel + backend deployment

- Frontend: `vercel deploy` from `frontend/` directory
- Backend: Deploy to Railway, Render, or Fly.io (FastAPI + uvicorn)
- Environment variables for API keys
- CORS configured for production domain

### Task 22: Precomputed demo data for new UI

- Run pipeline on all sample images through new API
- Cache results in `data/precomputed/`
- Pre-generate materials for demo students
- Ensure demo mode works without any API key

### Task 23: Update competition assets

- Update `docs/VIDEO-SCRIPT.md` for new UI flow
- Update `docs/COMPETITION-WRITEUP.md` with architecture changes
- New screenshots in `demo_assets/`
- Update Kaggle notebook

---

## Sprint 6: Video + Submission (Days 18-25)

### Task 24: Demo recording

- Record Add Student flow (IEP upload showcase)
- Record Scan Work flow (conversational capture)
- Record Material Generation (professional outputs)
- Record Dashboard (alerts, class overview)

### Task 25: Video production

- Follow updated `docs/VIDEO-SCRIPT.md`
- Sarah segments (classroom, talking-head)
- Jeff voiceover (architecture, technical depth)
- Edit to 180 seconds

### Task 26: Final submission

- Kaggle writeup
- GitHub repo cleanup
- Verify live URLs
- Submit

---

## Dependency Map

```
Task 1 (scaffold) 
  → Task 2 (students API)
  → Task 3 (capture API)
  → Task 4 (materials API)  
  → Task 5 (chat API) → Task 6 (alerts) → Task 7 (documents)

Task 8 (Next.js scaffold) → Task 10 (design system)
  → Task 9 (layout shell)
    → Task 11 (student page) → Task 12 (work + materials)
    → Task 13 (chat integration) → Task 14 (add student)

Task 15-18 (renderers) depend on Task 4 + Task 12

Task 19-23 (polish) depend on all above
```

**Parallelizable:** 
- Tasks 2-7 (all API routes) can be built sequentially in one sprint
- Tasks 8-10 (frontend scaffold) can start after Task 1, parallel to API work
- Tasks 15-18 (renderers) are independent of each other
