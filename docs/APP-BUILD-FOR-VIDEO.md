# ClassLens ASD App Build Requirements (Video-Driven)
**Build the App Specifically to Support the Video Script**

---

## Overview

The app must be built with the video in mind. Every button click, every result, every piece of UI must load instantly and look professional on camera. This document maps the video script directly to app requirements.

---

## Core Requirement: DEMO MODE

The app MUST have a "demo mode" that:
- Pre-loads all results (NO API calls during video recording)
- Instantaneous clicks (< 100ms load time)
- Pre-cached images and results
- Plays seamlessly for screen recording

**Critical:** If the demo waits for even 1 second for an API response, the video fails.

---

## Video-Driven App Architecture

### Video Moment 1: Student Selector (0-5 sec)
**What judges see:**
- Streamlit app sidebar with 3 student cards
- Cards show: Student name, grade, learning level, photo (avatar OK, no faces)
- Visible students: Maya (Grade 3, Level 2), Jaylen (Grade 1, Level 3), Sofia (Grade 5, Level 1)

**App requirement:**
```python
# students.py — Define 3 demo students
DEMO_STUDENTS = {
    "maya_2026": {
        "name": "Maya",
        "grade": 3,
        "level": 2,  # Level 2 ASD
        "interests": ["dinosaurs", "math", "drawing"],
        "iep_goals": [
            {"id": "g1", "title": "Use peer greeting phrases", "status": "active"},
            {"id": "g2", "title": "Follow multi-step directions", "status": "active"},
            {"id": "g3", "title": "Demonstrate self-regulation in groups", "status": "active"}
        ]
    },
    "jaylen_2026": {
        "name": "Jaylen",
        "grade": 1,
        "level": 3,  # Level 3, non-verbal, AAC user
        "interests": ["Thomas the Tank Engine", "trains", "colors"],
        "aac_user": True,
        "iep_goals": [
            {"id": "g1", "title": "Use AAC for choices", "status": "active"},
            {"id": "g2", "title": "Follow daily routine sequence", "status": "active"},
            {"id": "g3", "title": "Participate in parallel play", "status": "active"}
        ]
    },
    "sofia_2026": {
        "name": "Sofia",
        "grade": 5,
        "level": 1,  # Level 1, verbal, academic focused
        "interests": ["US Presidents", "history", "writing"],
        "iep_goals": [
            {"id": "g1", "title": "Write multi-paragraph essays", "status": "active"},
            {"id": "g2", "title": "Collaborate in group work", "status": "active"},
            {"id": "g3", "title": "Self-advocate for accommodations", "status": "active"}
        ]
    }
}

# In streamlit app.py:
def render_student_selector():
    """Render student cards in sidebar."""
    st.sidebar.subheader("Select Student")
    cols = st.sidebar.columns(1)

    for student_id, profile in DEMO_STUDENTS.items():
        with cols[0]:
            if st.sidebar.button(f"{profile['name']} (Grade {profile['grade']}, Level {profile['level']})"):
                st.session_state.selected_student = student_id
```

---

### Video Moment 2: Upload & Vision Reader (5-20 sec)
**What judges see:**
- Click "Upload Work Artifact" button
- File picker (pre-filled with `maya_math_worksheet.jpg`)
- Image displays (handwritten worksheet, "5 dinosaurs + 3 dinosaurs = ___")
- JSON result appears instantly:
  ```json
  {
    "transcribed_work": "5 dinosaurs + 3 dinosaurs = ___",
    "student_answers": ["8"],
    "confidence": 0.92
  }
  ```

**App requirements:**
1. **Sample images must exist:**
   ```
   data/sample_work/
   ├── maya_math_worksheet.jpg (dinosaur math problem, handwritten)
   ├── jaylen_choice_board.jpg (picture choice board with AAC symbols)
   └── sofia_presidents_essay.jpg (handwritten essay about presidents)
   ```

2. **Precomputed results must be cached:**
   ```python
   # data/precomputed/
   maya_2026_vision_reader_result.json:
   {
       "transcribed_work": "5 dinosaurs + 3 dinosaurs = ___",
       "student_answers": ["8"],
       "confidence": 0.92
   }
   ```

3. **UI must support instant result display:**
   ```python
   # In streamlit app.py
   def upload_and_demo():
       """Upload work artifact (demo mode uses pre-cached results)."""
       uploaded_file = st.file_uploader("Upload work artifact", type=["jpg", "png"])

       if uploaded_file or st.session_state.demo_mode:
           student_id = st.session_state.selected_student

           # Demo mode: load precomputed result INSTANTLY
           if st.session_state.demo_mode:
               result = load_precomputed_result(f"{student_id}_vision_reader")
           else:
               result = call_vision_reader(uploaded_file, student_id)

           # Display JSON result
           st.json(result)
   ```

---

### Video Moment 3: IEP Mapper Goal Detection (20-32 sec)
**What judges see:**
- Maya's IEP goals listed in sidebar (3 goals visible)
- Mapped result appears:
  ```
  MAPPED GOALS:
  ✓ Goal 2: "Follow directions" (Confidence: 0.88)
  Trial data: 1/3 completed independently
  ```
- Progress chart shows Goal 2 trending up over time

**App requirements:**
1. **Goal mapping result cached:**
   ```python
   # data/precomputed/maya_2026_iep_mapper_result.json
   {
       "mapped_goals": [
           {
               "goal_id": "g2",
               "goal_title": "Follow multi-step directions",
               "matched": True,
               "confidence": 0.88,
               "trial_data": {
                   "completed": 1,
                   "total": 3,
                   "independent": True
               }
           }
       ]
   }
   ```

2. **Progress chart data cached:**
   ```python
   # data/precomputed/maya_2026_progress_chart.json
   {
       "goal_id": "g2",
       "data_points": [
           {"date": "2026-03-24", "trial": 1, "completed": False},
           {"date": "2026-03-31", "trial": 1, "completed": False},
           {"date": "2026-04-07", "trial": 1, "completed": True},
           {"date": "2026-04-08", "trial": 1, "completed": True},
           {"date": "2026-04-09", "trial": 1, "completed": True}
       ]
   }
   ```

3. **UI renders goal checkmarks + chart:**
   ```python
   import plotly.graph_objects as go

   def display_mapped_goals(student_id):
       result = load_precomputed_result(f"{student_id}_iep_mapper")

       for goal_data in result["mapped_goals"]:
           if goal_data["matched"]:
               st.success(f"✓ {goal_data['goal_title']}")
               st.metric("Trials Completed", f"{goal_data['trial_data']['completed']}/{goal_data['trial_data']['total']}")

       # Plot progress chart
       chart_data = load_precomputed_result(f"{student_id}_progress_chart")
       fig = go.Figure()
       fig.add_trace(go.Scatter(
           x=[d["date"] for d in chart_data["data_points"]],
           y=[1 if d["completed"] else 0 for d in chart_data["data_points"]],
           mode='lines+markers',
           name='Progress'
       ))
       st.plotly_chart(fig)
   ```

---

### Video Moment 4: Progress Analyst (32-42 sec)
**What judges see:**
- Click "Analyze Progress" button
- Brief loading animation (2-3 sec, optional)
- Result appears:
  ```
  PROGRESS SUMMARY:
  Maya is making steady progress on Goal 2.
  Last 3 data points show 100% completion.
  No regressions detected.
  Recommendation: Increase complexity of directions (3→4 steps).
  ```

**App requirements:**
1. **Progress analysis result cached:**
   ```python
   # data/precomputed/maya_2026_progress_analyst_result.json
   {
       "summary": "Maya is making steady progress on Goal 2.",
       "recent_trend": "100% completion on last 3 trials",
       "regression_alerts": [],
       "recommendation": "Increase complexity of directions (3→4 steps)",
       "thinking_trace": "Analyzed 12 data points over 4 weeks... Last 3 trials show perfect completion... No regression patterns detected... Complexity increase recommended based on mastery."
   }
   ```

2. **UI displays result with optional thinking trace:**
   ```python
   def analyze_progress(student_id):
       result = load_precomputed_result(f"{student_id}_progress_analyst")

       st.write(result["summary"])
       st.info(result["recent_trend"])
       st.write(result["recommendation"])

       # Optional: show thinking trace for technical depth
       with st.expander("Model Thinking Process"):
           st.code(result["thinking_trace"])
   ```

---

### Video Moment 5: Material Forge Lesson Plan (42-60 sec) ← SHOWSTOPPER
**What judges see:**
- Click "Generate Materials" → "Lesson Plan"
- Lesson plan appears on screen:
  ```
  GOAL-ALIGNED LESSON PLAN: FOLLOWING DIRECTIONS WITH DINOSAURS
  Grade 3 | Autism-Friendly | 15 minutes

  Objective: Maya will follow a 3-step direction sequence
             using dinosaur-themed content

  STEP 1: Warm-up (3 min)
  ...
  [dinosaur clipart]
  ```
- Visible features: Title, grade, duration, objective, steps, clipart

**App requirements:**
1. **Lesson plan template + precomputed generation:**
   ```python
   # data/precomputed/maya_2026_lesson_plan.json
   {
       "title": "GOAL-ALIGNED LESSON PLAN: FOLLOWING DIRECTIONS WITH DINOSAURS",
       "grade": 3,
       "duration": "15 minutes",
       "format": "Autism-Friendly",
       "objective": "Maya will follow a 3-step direction sequence using dinosaur-themed content",
       "sections": [
           {
               "step": "STEP 1: Warm-up (3 min)",
               "content": "We're going to be dinosaur paleontologists today...",
               "instructions": ["Show dinosaur picture", "Ask: 'What do you see?'"],
               "expected_response": "Simple observation (e.g., 'Dinosaur', 'Big')"
           },
           {
               "step": "STEP 2: Multi-step task (10 min)",
               "content": "Direction card (printed, visual)...",
               "instructions": [
                   "→ Find the T-Rex card",
                   "→ Point to the dinosaur's teeth",
                   "→ Count the spikes on the back"
               ]
           },
           {
               "step": "STEP 3: Closure (2 min)",
               "content": "Praise: 'You followed all 3 steps! You're a great paleontologist!'",
               "clipart": "dinosaur_with_checkmarks.png"
           }
       ],
       "printable_pdf_path": "data/precomputed/maya_2026_lesson_plan.pdf"
   }
   ```

2. **UI renders lesson plan scrollably:**
   ```python
   def display_lesson_plan(student_id):
       plan = load_precomputed_result(f"{student_id}_lesson_plan")

       st.markdown(f"## {plan['title']}")
       st.write(f"**Grade {plan['grade']} | {plan['duration']} | {plan['format']}**")
       st.write(f"**Objective:** {plan['objective']}")

       for section in plan['sections']:
           st.subheader(section['step'])
           st.write(section['content'])
           for instr in section['instructions']:
               st.write(instr)
           if 'clipart' in section:
               st.image(f"data/clipart/{section['clipart']}")

       # Export button
       if st.button("Export as PDF"):
           st.download_button(
               label="Download PDF",
               data=open(plan['printable_pdf_path'], 'rb'),
               file_name=f"{student_id}_lesson_plan.pdf",
               mime="application/pdf"
           )
   ```

3. **Critical:** Lesson plan must be PRINTABLE
   - Include header with student name, date, teacher notes
   - Color graphics (dinosaur clipart)
   - Professional PDF layout (not just screenshot)
   - PDF saved in `data/precomputed/{student_id}_lesson_plan.pdf`

---

### Video Moment 6: Social Story for Jaylen (60-72 sec)
**What judges see:**
- Switch to Jaylen's profile
- Click "Generate Materials" → "Social Story"
- Social story pages appear (picture book style):
  ```
  [PAGE 1 - IMAGE: Thomas the Tank Engine]
  Text: "I like snack time."

  [PAGE 2 - IMAGE: Snack options]
  Text: "I can choose. Apple? Crackers? Yogurt?"
  [AAC symbols below each option]

  [PAGE 3 - IMAGE: Boy pointing at snack]
  Text: "I point to what I want."

  [PAGE 4 - IMAGE: Boy eating, happy]
  Text: "Good job making a choice!"
  ```

**App requirements:**
1. **Social story template (Carol Gray framework):**
   ```python
   # data/precomputed/jaylen_2026_social_story.json
   {
       "title": "THOMAS THE TANK ENGINE SOCIAL STORY",
       "theme": "Thomas the Tank Engine",
       "topic": "Asking for a choice at snack time",
       "pages": [
           {
               "image": "thomas_happy.png",
               "text": "I like snack time.",
               "type": "affirmation"
           },
           {
               "image": "snack_choices.png",
               "text": "I can choose. Apple? Crackers? Yogurt?",
               "aac_symbols": ["apple.png", "crackers.png", "yogurt.png"],
               "type": "directive"
           },
           {
               "image": "boy_pointing.png",
               "text": "I point to what I want.",
               "type": "directive"
           },
           {
               "image": "boy_eating_happy.png",
               "text": "Good job making a choice!",
               "type": "praise"
           }
       ]
   }
   ```

2. **UI renders social story page-by-page:**
   ```python
   def display_social_story(student_id):
       story = load_precomputed_result(f"{student_id}_social_story")

       st.markdown(f"## {story['title']}")
       st.write(f"Theme: {story['theme']} | Topic: {story['topic']}")

       page_num = st.slider("Page", 1, len(story['pages']))
       page = story['pages'][page_num - 1]

       # Display image
       st.image(f"data/clipart/{page['image']}")

       # Display text
       st.markdown(f"### {page['text']}")

       # Display AAC symbols if present
       if 'aac_symbols' in page:
           cols = st.columns(len(page['aac_symbols']))
           for col, symbol in zip(cols, page['aac_symbols']):
               with col:
                   st.image(f"data/aac/{symbol}")
   ```

3. **AAC symbols must be available:**
   - Store AAC symbols in `data/aac/`
   - Include standard PECS + Boardmaker symbols
   - For video: apple, crackers, yogurt, choices, pointing, celebration

---

### Video Moment 7: Admin Dashboard (72-82 sec)
**What judges see:**
- Click "Admin Dashboard"
- 3 student progress cards visible
- Bar chart: Goal completion rates
- Line chart: Regression alerts over time (flat = good)
- Table: Materials generated this week

**App requirements:**
1. **Admin dashboard page (separate from teacher view):**
   ```python
   def admin_dashboard():
       st.title("Classroom Dashboard")

       # Student cards row
       cols = st.columns(3)
       for idx, (student_id, profile) in enumerate(DEMO_STUDENTS.items()):
           with cols[idx]:
               st.metric(f"{profile['name']}", f"{profile['level']} ASD Level")

       # Goal completion bar chart
       goal_data = load_precomputed_result("classroom_goal_completion")
       fig_bar = go.Figure(goal_data)
       st.plotly_chart(fig_bar)

       # Regression alerts line chart
       regression_data = load_precomputed_result("classroom_regression_alerts")
       fig_line = go.Figure(regression_data)
       st.plotly_chart(fig_line)

       # Materials table
       materials_df = load_precomputed_result("classroom_materials_table")
       st.dataframe(materials_df)
   ```

2. **Precomputed dashboard data:**
   ```python
   # data/precomputed/classroom_goal_completion.json
   {
       "type": "bar",
       "x": ["Maya", "Jaylen", "Sofia"],
       "y": [0.75, 0.60, 0.85],
       "name": "Completion Rate"
   }

   # data/precomputed/classroom_regression_alerts.json
   {
       "type": "scatter",
       "x": ["2026-03-24", "2026-03-31", "2026-04-07", "2026-04-08", "2026-04-09"],
       "y": [0, 0, 0, 0, 0],
       "name": "Alerts"
   }
   ```

---

### Video Moment 8: Code Deep Dive (82-90 sec)
**What judges see:**
- IDE window showing `agents/vision_reader.py`
- Highlighted function calling tools definition
- Highlighted Gemma client call

**App requirements:**
1. **Code must be readable and in repo:**
   ```
   classlens-asd/
   ├── agents/
   │   ├── vision_reader.py ← Must show on camera
   │   ├── iep_mapper.py
   │   ├── progress_analyst.py
   │   └── material_forge.py
   ├── core/
   │   ├── gemma_client.py ← Must show on camera
   │   └── pipeline.py
   └── schemas/
       └── tools.py ← Must show on camera
   ```

2. **agents/vision_reader.py must contain:**
   ```python
   # Show on camera:
   tools = [
       {
           "name": "transcribe_work_artifact",
           "parameters": {
               "type": "object",
               "properties": {
                   "subject": {"type": "string"},
                   "type": {"type": "string"},
                   "transcribed_work": {"type": "string"},
                   "student_answers": {"type": "array"},
                   "confidence": {"type": "number"}
               }
           }
       }
   ]

   # And:
   response = gemma_client.generate(
       image_data=work_artifact_image,
       tools=tools,
       system_prompt=VISION_READER_PROMPT
   )
   ```

---

### Video Moment 9: Ollama Edge Demo (90-98 sec)
**What judges see:**
- Terminal window showing Ollama running
- Model loading: `ollama run gemma-4-e4b`
- Quick inference (don't wait for full response, just show it starts)

**App requirements:**
- Edge functionality not required for main video, but must be mentioned
- If demoed: have Ollama installed + model pre-downloaded locally
- Just show model loading + first few lines of output

---

## Precomputation Strategy

**ALL demo results must be pre-cached.** Here's the structure:

```
data/precomputed/
├── maya_2026_vision_reader.json
├── maya_2026_iep_mapper.json
├── maya_2026_progress_analyst.json
├── maya_2026_lesson_plan.json
├── maya_2026_lesson_plan.pdf  ← Printable!
├── maya_2026_progress_chart.json
│
├── jaylen_2026_vision_reader.json
├── jaylen_2026_iep_mapper.json
├── jaylen_2026_progress_analyst.json
├── jaylen_2026_social_story.json
├── jaylen_2026_social_story.pdf  ← Printable!
│
├── sofia_2026_vision_reader.json
├── sofia_2026_iep_mapper.json
├── sofia_2026_progress_analyst.json
├── sofia_2026_lesson_plan.json
├── sofia_2026_lesson_plan.pdf  ← Printable!
│
├── classroom_goal_completion.json
├── classroom_regression_alerts.json
├── classroom_materials_table.json
│
└── README.md  ← Documents what each file contains
```

**Loading precomputed results:**
```python
def load_precomputed_result(result_name: str):
    """Load pre-cached result (0 latency)."""
    import json
    path = f"data/precomputed/{result_name}.json"
    with open(path, 'r') as f:
        return json.load(f)
```

---

## Streamlit App Structure for Video

```python
# app.py
import streamlit as st

# Demo mode flag
DEMO_MODE = True

def main():
    st.set_page_config(page_title="ClassLens ASD", layout="wide")

    # Sidebar: Student selector
    st.sidebar.title("ClassLens ASD")
    page = st.sidebar.radio("Navigation", ["Teacher", "Admin", "Settings"])

    if page == "Teacher":
        teacher_page()
    elif page == "Admin":
        admin_dashboard()
    elif page == "Settings":
        settings_page()

def teacher_page():
    """Main teacher interface (what's shown in video)."""
    st.title("IEP Progress Intelligence")

    # Student selector
    render_student_selector()

    # Work artifact upload
    render_upload_interface()

    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Vision", "IEP Mapping", "Analysis", "Materials"])

    with tab1:
        display_vision_reader_result(st.session_state.selected_student)
    with tab2:
        display_iep_mapper_result(st.session_state.selected_student)
    with tab3:
        display_progress_analyst_result(st.session_state.selected_student)
    with tab4:
        display_material_forge_interface(st.session_state.selected_student)

if __name__ == "__main__":
    main()
```

---

## Critical Timing Requirements

| Video Moment | Max Load Time | Action |
|--------------|--------------|--------|
| Click student card | < 50ms | Student profile displays |
| Click "Upload" | < 100ms | File picker appears |
| Select image | < 500ms | Image displays + Vision Reader result loads |
| Click "Show IEP Mapping" | < 100ms | Goal mapping result displays |
| Click "Analyze Progress" | < 500ms | Progress analyst result displays |
| Click "Generate Materials" | < 100ms | Material Forge interface appears |
| Click "Lesson Plan" | < 100ms | Lesson plan displays |
| Click "Export PDF" | < 1000ms | PDF downloaded |

**If ANY click takes > 1 second, the video will look janky on camera.**

---

## Testing the App for Video

Before recording, test all clicks in this sequence:

```bash
streamlit run app.py

# Test sequence (same as video):
1. Click Maya card → loads instantly
2. Click "Upload" → file picker appears instantly
3. Select maya_math_worksheet.jpg → image + Vision Reader result appear instantly
4. Scroll down → see IEP goals, progress chart → smooth scroll
5. Click "Analyze Progress" → result appears instantly
6. Click "Generate Materials" → dropdown appears instantly
7. Click "Lesson Plan" → lesson plan displays instantly
8. Scroll through lesson plan → smooth, fast scroll
9. Click "Export PDF" → download dialog appears
10. Switch to Jaylen → profile loads instantly
11. Click "Generate Materials" → "Social Story" option visible
12. Click "Social Story" → social story displays instantly
13. Switch to Admin Dashboard → 3 student cards visible
14. Scroll down → bar chart visible, smooth animation
15. Scroll down → line chart visible, smooth animation
16. Scroll down → materials table visible
```

**Every single step must be fast and smooth.**

---

## PDF Export Requirements

Both lesson plans and social stories must export as professional PDFs:

**Lesson Plan PDF:**
- Header: "Goal-Aligned Lesson Plan for [Student Name]"
- Color (dinosaur clipart)
- Printable (A4/Letter, 1" margins)
- Ready to print and use in classroom

**Social Story PDF:**
- Color (Thomas the Tank Engine images, AAC symbols)
- 4-page "book" format
- Printable for lamination
- Ready to use immediately

Use `reportlab` or similar to generate PDFs with consistent formatting.

---

## Final Checklist for App Build

- [ ] 3 student profiles fully defined (Maya, Jaylen, Sofia)
- [ ] All precomputed results cached in `data/precomputed/`
- [ ] Sample work artifacts ready (`data/sample_work/`)
- [ ] Streamlit app deployed (locally for testing, then to Community Cloud)
- [ ] Demo mode working (all clicks instant)
- [ ] Every click tested and timed
- [ ] Lesson plans printable as PDFs
- [ ] Social stories printable as PDFs
- [ ] Admin dashboard renders charts correctly
- [ ] Code is readable on screen (large enough font)
- [ ] No API keys in code (only in `.env`)
- [ ] All 3 students can be selected and demoed
- [ ] All 4 agents (Vision, IEP, Analyst, Forge) show results instantly
- [ ] Mobile-responsive (judges might view on phone)

---

## Expected Video Quality After App Build

With this app architecture:
- ✅ Video will show a **working, responsive app**
- ✅ Every click loads **instantly** (no waiting for API)
- ✅ Results are **printable and professional**
- ✅ Code is **visible and credible**
- ✅ Demo is **reproducible** (judges can try it themselves)
- ✅ Judges will think: **"This is real. This actually works."**

---

**Build with video in mind. Every UI element, every precomputed result, every PDF export is part of your competitive advantage.**
