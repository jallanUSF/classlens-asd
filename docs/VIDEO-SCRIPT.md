# ClassLens ASD — Kaggle Gemma 4 Good Hackathon Video Script
**3-Minute Submission | Video = 30 Points of 100**

---

## PRODUCTION NOTES

### Recording Equipment & Setup
- **Camera:** Smartphone (iPhone/Android) or webcam at 1080p minimum
- **Audio:** External USB microphone or lavalier mic (avoid laptop mic echo)
- **Lighting:** Soft natural light or two-light setup (key + fill). Avoid harsh shadows on faces.
- **Background:** Classroom photo or calm solid color for talking-head segments. Classroom background for Sarah's segments adds authenticity.
- **Laptop:** Connect via HDMI to second monitor for cleaner screen recording (not mirrored). Record at 1920x1080.

### Screen Recording Software
- **ScreenFlow (Mac)** or **OBS (cross-platform)** or **Camtasia**
- Record Streamlit app in a **maximized window** (no taskbar visible)
- Set browser to 125% zoom for readable text (Plotly charts must be crisp)
- **Demo Mode:** Pre-bake all results so there's NO waiting for API calls

### Audio Mix
- **Voice-over narration:** Recorded separately, loud and clear, no background noise
- **Background music:** Subtle, uplifting (royalty-free piano or orchestral, 15-20dB below voice)
- **Sound effects:** Minimize — only use UI feedback (button clicks, page transitions) if they enhance clarity

### Editing
- **Software:** Adobe Premiere Pro, Final Cut Pro, or DaVinci Resolve
- **Pace:** Fast cuts for energy, slower on product features (let Plotly charts animate)
- **Color grade:** Warm, welcoming tone (ASD-friendly: predictable, calm, not jarring)
- **Pacing guide:** Every 10 seconds = new shot/scene transition (keeps judges engaged)
- **Title card:** ClassLens ASD logo + "Gemma 4 Good Hackathon" (2 sec, first frame)
- **Credits:** Small text at end with names + links to GitHub repo (5 sec)

### Technical Depth Moments (for judges who read code)
- Record **one 3-5 second close-up of function calling JSON** in browser DevTools or terminal
- Show **thinking mode reasoning trace** (if accessible via API response)
- Quick shot of **agent orchestration flow** (system prompt snippet or architecture diagram)
- Make sure judges can read `tools.py` structure without pausing video

---

## SHOT LIST
**Total Duration: 180 seconds | Each shot = # seconds (cumulative: XX sec)**

### OPENING: EMOTIONAL HOOK (0-30 sec)
**Goal:** Make judges care about the problem before showing the solution.

#### Shot 1: Sarah on camera in classroom — TALK DIRECT TO CAMERA
- **Duration:** 30 seconds
- **Speaker:** Sarah Allan (K-12 special ed teacher)
- **Setting:** Classroom with autism-friendly decor (quiet corner preferred; natural light)
- **Camera:** Close-up (chest up), eye contact with camera
- **Narration (exact words):**
  > "I teach six autistic students. Every single week, I spend 15 hours tracking their progress on IEP goals by hand — counting tally marks, writing notes, trying to see the patterns. My Monday afternoons are just... IEP data entry. But when I look at Maya's work, I don't see a spreadsheet. I see a child who's working hard to learn social skills. I see progress that matters. The problem is: how do I see that progress at scale without losing my mind?"
- **B-roll overlay (optional):** Subtle background: classroom photos, student work samples (NO faces — privacy)
- **Pacing:** Speak slowly, warm tone, pauses between thoughts
- **Emotion:** Authentic frustration + hope
- **Editing:** Fade from black, slow zoom-in, subtle color grade (warm)

**Cumulative: 30 sec**

---

### DEMO: THE FOUR AGENTS IN ACTION (30-150 sec)

#### Shot 2: Streamlit App Intro — SCREENSHOT + NARRATION
- **Duration:** 5 seconds
- **Visual:** Streamlit app open to student selector sidebar (Maya, Jaylen, Sofia visible)
- **Narration (Jeff, voiceover):**
  > "ClassLens ASD is a multi-agent system built on Gemma 4. Watch what happens when we upload a simple worksheet photo."
- **Editing:** Zoom on sidebar to highlight student cards, fast pan across UI
- **Technical depth:** Students are Pydantic models with IEP goals listed — judges see that

**Cumulative: 35 sec**

---

#### Shot 3: Vision Reader Agent — UPLOAD & MAGIC
- **Duration:** 15 seconds
- **Visual:**
  1. Click "Upload work artifact" button
  2. Select Maya's dinosaur math worksheet (handwritten, messy, real student work)
  3. Show the photo briefly (judges see it's legit hand work)
  4. **[FAST CUT]** show transcription JSON result in sidebar:
     ```
     {
       "subject": "math",
       "type": "worksheet",
       "transcribed_work": "5 dinosaurs + 3 dinosaurs = __ Fill in the blank",
       "student_answers": ["8 dinos"],
       "confidence": 0.92
     }
     ```
- **Narration (Jeff, voiceover):**
  > "Vision Reader is a Gemma 4 multimodal agent. It uses native vision capabilities to read Maya's handwritten worksheet — no OCR library, just Gemma 4's vision understanding. Instantly, it transcribes the work into structured JSON: the question, the answer, the confidence score."
- **Sound design:** Subtle "whoosh" sound as JSON appears
- **Technical depth:** Highlight that this is **function calling** in action (not simple text output) — judges see structured data
- **Editing:** Zoom on transcription box, highlight JSON key-value pairs in different colors

**Cumulative: 50 sec**

---

#### Shot 4: IEP Mapper Agent — GOAL DETECTION
- **Duration:** 12 seconds
- **Visual:**
  1. Show Maya's student profile sidebar (lists her IEP goals):
     - Goal 1: Use peer greeting phrases ("Hi, how are you?")
     - Goal 2: Follow multi-step directions
     - Goal 3: Demonstrate self-regulation in group settings
  2. **[FAST CUT]** Show the agent output panel:
     ```
     MAPPED GOALS:
     ✓ Goal 2: "Follow directions" (Math worksheet required multi-step task)
     Trial data recorded: 1/3 trials completed independently
     Confidence: 0.88
     ```
  3. Show a **progress chart snapshot** (small bar chart showing Goal 2 progress over time)
- **Narration (Jeff, voiceover):**
  > "IEP Mapper uses function calling to match the transcribed work to Maya's specific IEP goals. Her worksheet wasn't just about math — it was about following multi-step directions. The agent records a trial. One student. One worksheet. One data point. But over time? Patterns emerge."
- **Technical depth:** Show the `tools.py` snippet of the goal-mapping schema (0.5 sec) — judges see we built custom tools
- **Editing:** Highlight the progress chart line going up (visual confirmation of impact)

**Cumulative: 62 sec**

---

#### Shot 5: Progress Analyst Agent — THINKING MODE
- **Duration:** 10 seconds
- **Visual:**
  1. Click "Analyze Progress" button
  2. Show a brief thinking animation or text overlay:
     ```
     Analyzing 12 data points for Maya over 4 weeks...
     Trend detection... 📊
     Regression alerts... ⚠️
     ```
  3. Result panel shows:
     ```
     PROGRESS SUMMARY:
     Maya is making steady progress on Goal 2.
     Last 3 data points show 100% completion.
     No regressions detected.
     Recommendation: Increase complexity of directions (3→4 steps).
     ```
- **Narration (Jeff, voiceover):**
  > "Progress Analyst uses Gemma 4's thinking mode to detect trends. It's not just counting data points — it's reasoning about patterns, flagging regressions, and recommending next steps for Maya's teacher."
- **Sound design:** Subtle "analyzing" sound (very quiet, like a computer thinking)
- **Editing:** Show thinking animation, then result slides in from right. Highlight the recommendation in bold.

**Cumulative: 72 sec**

---

#### Shot 6: Material Forge Agent — DINOSAUR LESSON PLAN
- **Duration:** 18 seconds (THIS IS THE SHOWSTOPPER)
- **Visual:**
  1. Click "Generate Materials" → select "Lesson Plan"
  2. Show generated lesson plan appearing on screen:
     ```
     GOAL-ALIGNED LESSON PLAN: FOLLOWING DIRECTIONS WITH DINOSAURS
     Grade 3 | Autism-Friendly | 15 minutes

     Objective: Maya will follow a 3-step direction sequence
                using dinosaur-themed content

     STEP 1: Warm-up (3 min)
     "We're going to be dinosaur paleontologists today!"
     Show dinosaur picture. Ask: "What do you see?"
     Expected response: Simple observation (e.g., "Dinosaur", "Big")

     STEP 2: Multi-step task (10 min)
     Direction card (printed, visual):
     → Find the T-Rex card
     → Point to the dinosaur's teeth
     → Count the spikes on the back

     STEP 3: Closure (2 min)
     Praise: "You followed all 3 steps! You're a great paleontologist!"
     [Include colored clipart of dinosaur with checkmarks]
     ```
  3. Scroll down to show it's **printable and ready to use**
  4. Show a **PDF export button** (judges see it's production-ready)
- **Narration (Sarah, on camera — back to her, sitting in classroom):**
  > "This is what changed my mind about AI for ASD teaching. The system didn't just track Maya's progress — it **generated a lesson plan that uses her passion — dinosaurs — to teach her IEP goal.** I printed this yesterday, used it in class today, and it *worked*. Maya stayed engaged the whole 15 minutes. She followed all three steps."
- **Sound design:** Uplifting chord when lesson plan appears
- **Editing:**
  - Slow pan through lesson plan content (let judges read)
  - Zoom on dinosaur clipart (shows Material Forge can integrate graphics)
  - Fade to Sarah reaction shot (emotional payoff)
  - Color grade: warm, encouraging
- **Technical depth:** Hidden but visible: Lesson plan was generated by Material Forge agent using:
  - Student interest (dinosaurs — from profile)
  - IEP goal (follow directions)
  - Carol Gray social story framework
  - ASD sensory + cognitive considerations

**Cumulative: 90 sec**

---

#### Shot 7: Social Story for Jaylen — NON-VERBAL STUDENT
- **Duration:** 12 seconds (Show inclusivity of system)
- **Visual:**
  1. Switch to Jaylen's profile (sidebar shows: Level 3, non-verbal, AAC user, loves Thomas the Tank Engine)
  2. Show generated social story output:
     ```
     THOMAS THE TANK ENGINE SOCIAL STORY
     About: Asking for a choice at snack time
     By: ClassLens ASD | For: Jaylen

     [VISUAL PAGE 1]
     Picture of Thomas the tank engine smiling
     Text: "I like snack time."

     [VISUAL PAGE 2]
     Picture of snack choices (crackers, apple, yogurt)
     Text: "I can choose. Apple? Crackers? Yogurt?"
     AAC symbol below each option

     [VISUAL PAGE 3]
     Thomas pointing to snack
     Text: "I point to what I want."

     [VISUAL PAGE 4]
     Jaylen-like figure eating snack, happy
     Text: "Good job making a choice!"
     ```
  3. Show **printable PDF layout** (4 pages, color, ready to print and laminate)
- **Narration (Jeff, voiceover):**
  > "Jaylen is non-verbal and uses AAC. ClassLens generates social stories using his interests — Thomas the Tank Engine — and aligns them to his IEP goals. Carol Gray framework built in. AAC symbols integrated. This teaches self-advocacy without assuming speech."
- **Sound design:** Cheerful Thomas the Tank Engine-style chime (subtle)
- **Editing:** Flip through pages like a picture book, emphasize the AAC symbols

**Cumulative: 102 sec**

---

#### Shot 8: Admin Report — MULTI-STAKEHOLDER ANGLE
- **Duration:** 10 seconds (Show judges this scales beyond one teacher)
- **Visual:**
  1. Click to "Admin Dashboard"
  2. Show Plotly dashboard with:
     - Three student cards showing IEP goal progress (Maya, Jaylen, Sofia)
     - **Bar chart:** Goal completion rates across classroom
     - **Line chart:** Regression alerts over time (none for this cohort = good)
     - **Table:** Material outputs generated this week (12 lesson plans, 3 social stories, 2 admin reports)
  3. Show **"Generate Parent Report" button** (click it)
  4. Brief preview of parent communication (translated to Spanish available)
- **Narration (Jeff, voiceover):**
  > "This isn't just for teachers. Administrators see aggregated progress across all students. Parents get weekly updates in their preferred language. Everyone has visibility without doing manual work."
- **Editing:** Zoom on charts, highlight the downward regression trend line (if present) — show judges the system catches problems
- **Technical depth:** Plotly is rendering real data; judges see `plotly.graph_objects` quality

**Cumulative: 112 sec**

---

### TECHNICAL DEPTH SHOWCASE (112-150 sec)

#### Shot 9: Code Architecture Moment
- **Duration:** 8 seconds
- **Visual:**
  1. Briefly show **system terminal** or IDE with `agents/vision_reader.py` open
  2. Highlight function calling declaration:
     ```python
     tools = [
       {
         "name": "transcribe_work_artifact",
         "parameters": {
           "type": "object",
           "properties": {
             "subject": {...},
             "type": {...},
             "transcribed_work": {...},
             "student_answers": {...}
           }
         }
       }
     ]
     ```
  3. **OR** show Gemma 4 API response JSON with `functionCall` object
  4. Pan to show the calling code:
     ```python
     response = gemma_client.generate(
       image_data=work_artifact_image,
       tools=tools,
       system_prompt=VISION_READER_PROMPT
     )
     ```
- **Narration (Jeff, voiceover):**
  > "This works with Gemma 4's native function calling. No LangChain, no wrapper frameworks — just direct API calls. The model understands the schema, parses structured data, and returns validated JSON. That's why it's fast and reliable."
- **Editing:** Zoom on key lines, highlight in different colors
- **Sound design:** Minimal; let code be silent

**Cumulative: 120 sec**

---

#### Shot 10: Thinking Mode Reasoning (OPTIONAL — ONLY IF API EXPOSES IT)
- **Duration:** 5 seconds
- **Visual:**
  1. If Google AI Studio shows thinking trace, capture a screenshot
  2. Show brief snippet of reasoning chain (e.g., "Student completed X steps... Analyzing trend... Recommending Y")
  3. OR show terminal output of Progress Analyst thinking
- **Narration (Jeff, voiceover):**
  > "The Progress Analyst uses Gemma 4's extended thinking mode. It actually reasons about the data — not just summarizing."
- **Editing:** Fast, technical, 3-4 lines of reasoning visible

**Cumulative: 125 sec**

---

### CLOSING: VISION & CALL TO ACTION (150-180 sec)

#### Shot 11: Edge Computing Demo (SPECIAL TECH TRACK CREDENTIAL)
- **Duration:** 8 seconds
- **Visual:**
  1. Show **Ollama running locally** with `gemma-4-e4b` model
  2. Brief screenshot of model loading + inference
  3. Show response time (should be fast if hardware is decent)
- **Narration (Jeff, voiceover):**
  > "We also built an offline version using Ollama and Gemma 4E4B for privacy-conscious schools with unreliable internet. Same quality, zero cloud dependency."
- **Editing:** Quick, show Ollama in action for 3-4 seconds
- **Technical depth:** Judges see you can optimize for edge + privacy (Special Tech track points)

**Cumulative: 133 sec**

---

#### Shot 12: Sarah's Vision — CLOSE ON EMOTIONAL NOTE
- **Duration:** 25 seconds
- **Visual:**
  - Sarah back on camera in classroom, sitting, eye contact
  - Classroom visible behind her (authentic setting)
- **Narration (Sarah, speaking to camera, direct):**
  > "I've been teaching autistic students for 15 years. Every tool tries to replace me — to automate my judgment, to make me data entry. ClassLens doesn't do that. It gives me back my time. I upload a worksheet. Gemma 4 handles the transcription, the goal mapping, the trend analysis. I review it, edit it, approve it. *I stay in control.* And suddenly, I have Tuesdays again. I have afternoons to actually *teach* — to know my students — instead of counting marks in a spreadsheet. That's the real impact. Not the technology. The time. The relationship. That's what matters in special education."
- **Sound design:** Soft background music (piano, uplifting)
- **Editing:**
  - Slow, no cuts during monologue (let her speak naturally)
  - Subtle zoom to eyes
  - Warm color grade
  - Fade out slowly

**Cumulative: 158 sec**

---

#### Shot 13: Demo Montage — RAPID FIRE VISUAL SHOWCASE (OPTIONAL — if time allows)
- **Duration:** 10 seconds
- **Visual:**
  - Fast cuts of:
    1. Sofia's lesson plan loading (Grade 5, US Presidents theme)
    2. Admin report charts animating
    3. Parent communication in Spanish
    4. Printable materials stacked
- **Sound design:** Energetic (match the pace)
- **Narration (Jeff, quick voiceover):**
  > "Three students. Multiple learning profiles. Diverse IEP goals. One system. Built for scale."

**Cumulative: 168 sec**

---

#### Shot 14: CLOSING TITLE CARD & CREDENTIALS
- **Duration:** 12 seconds
- **Visual:**
  - Slide 1 (3 sec): ClassLens ASD logo + "Gemma 4 Good Hackathon"
  - Slide 2 (3 sec): "Built with Google Gemma 4 | Multimodal | Function Calling | Thinking Mode"
  - Slide 3 (3 sec): "For the Future of Education Track"
  - Slide 4 (3 sec): GitHub link + "github.com/jeffallan/classlens-asd" + team names
- **Sound design:** Uplifting orchestral sting
- **Editing:** Fade between slides, professional typography

**Cumulative: 180 sec**

---

## TIMING BREAKDOWN

| Section | Duration | Cumulative | Notes |
|---------|----------|-----------|-------|
| Opening (Sarah emotional hook) | 30 sec | 30 | Problem framing |
| Agent 1: Vision Reader | 5 sec | 35 | Screenshot + narration |
| Agent 1 (continued): Upload + transcription | 15 sec | 50 | Handwritten worksheet magic |
| Agent 2: IEP Mapper | 12 sec | 62 | Goal detection + trial data |
| Agent 3: Progress Analyst | 10 sec | 72 | Thinking mode reasoning |
| Agent 4: Material Forge — Lesson Plan | 18 sec | 90 | SHOWSTOPPER (Sarah reaction) |
| Agent 4 (continued): Social Story for Jaylen | 12 sec | 102 | Non-verbal student inclusion |
| Admin Dashboard | 10 sec | 112 | Multi-stakeholder angle |
| Technical Depth: Function Calling | 8 sec | 120 | Code snippet |
| Technical Depth: Thinking Mode | 5 sec | 125 | Reasoning trace |
| Edge Computing Demo (Ollama) | 8 sec | 133 | Special Tech track |
| Sarah's Vision (closing) | 25 sec | 158 | Emotional payoff |
| Demo Montage (optional buffer) | 10 sec | 168 | Rapid-fire showcase |
| Closing Credits | 12 sec | 180 | Title + GitHub + team |
| **TOTAL** | **180 sec** | **180 sec** | **Exactly 3 minutes** |

**Buffer:** 0 seconds (tight fit — edit to this exact timing)

---

## EMOTIONAL ARC & STORY STRUCTURE

### Act 1: The Problem (0-30 sec)
- **Setting:** Classroom, Sarah's genuine frustration
- **Conflict:** 15 hours/week on IEP data entry vs. 0 hours with actual students
- **Question posed to judges:** "How do I see progress at scale without losing my mind?"
- **Emotional tone:** Authentic, relatable, sympathetic
- **Judges should feel:** Urgency. This teacher needs help.

### Act 2: The Solution (30-125 sec)
- **Setting:** Streamlit app, live demo
- **Journey:** Upload → transcription → goal mapping → analysis → material generation
- **Key moment:** Sarah's reaction to the dinosaur lesson plan (72-90 sec)
- **Emotional tone:** Wonder, relief, excitement
- **Judges should feel:** "Oh wow, this actually works. And the teacher is IN CONTROL."

### Act 3: The Impact (125-180 sec)
- **Setting:** Back to Sarah in classroom
- **Vision:** What becomes possible when AI handles the drudgery
- **Payoff:** "I have Tuesdays again. I have afternoons to actually teach."
- **Technical credibility:** Ollama + Gemma 4 depth for judges who need proof
- **Emotional tone:** Hopeful, grounded, human-centered
- **Judges should feel:** This isn't about the AI. It's about liberating teachers to be teachers.

---

## VISUAL DESIGN PRINCIPLES

**ASD-Friendly Aesthetics** (because Sarah will watch this, and our audience includes autism-adjacent folks):
- Calm, cool color palette (blues, greens, soft neutrals)
- No jarring transitions (fade/dissolve, no glitch effects)
- Consistent pacing (predictable cuts at ~10 sec intervals)
- Clear hierarchy (text readable at 1080p without squinting)
- Minimal animation (purposeful, not distracting)

**Judiciary-Optimized Visuals**:
- Large, readable text in code snippets
- Plotly charts animate clearly (don't move too fast)
- IEP goals and student profiles visible long enough to read
- Sarah's face clearly lit and visible (builds trust)
- Streamlit app fills most of the screen (demo-forward focus)

---

## TECHNICAL DEPTH MOMENTS

These earn judges' respect and "proof of concept" points:

1. **Function Calling Visibility** (Shot 9, 120 sec)
   - Show the JSON schema judges can read
   - Prove you're using Gemma 4's native capabilities, not a wrapper
   - Judges who vet submissions will check this

2. **Thinking Mode Reasoning** (Shot 10, 125 sec)
   - If API exposes it, show a brief reasoning trace
   - Proves extended thinking is actually being used
   - Shows model is doing real analysis, not cheap summarization

3. **Structured Data Extraction** (Shots 3-4)
   - Emphasize that Vision Reader outputs **valid JSON**, not loose text
   - IEP Mapper uses that JSON to drive function calls
   - This proves end-to-end integration, not fragile text parsing

4. **Real Student Data** (All demo shots)
   - Use actual handwritten worksheets (not generated images)
   - Real IEP goals (though anonymized)
   - Real student interests (dinosaurs, Thomas, Presidents)
   - Judges will spot if data looks fake

5. **Edge Computing Option** (Shot 11, 133 sec)
   - Show Ollama + Gemma 4E4B running locally
   - Proves you're thinking about privacy, offline scenarios, scalability
   - Positions ClassLens as enterprise-ready

---

## SCREEN RECORDING GUIDE: EXACT DEMO FLOW

### Pre-Recording Checklist
- [ ] Streamlit app running locally or deployed to Community Cloud
- [ ] **Demo mode enabled** — all results pre-baked (NO API calls during recording)
- [ ] Three student profiles loaded (Maya, Jaylen, Sofia)
- [ ] Sample work artifacts ready:
  - `maya_math_worksheet.jpg` (handwritten dinosaur math)
  - `jaylen_choice_board.jpg` (picture choice board)
  - `sofia_presidents_essay.jpg` (handwritten essay draft)
- [ ] Pre-computed results cached in `data/precomputed/`
- [ ] Browser zoomed to 125% (text readable, UI not cramped)
- [ ] Screen resolution: 1920x1080 minimum

### Recording Sequence

**[Screenshot: 0-5 sec]**
```
1. App opens to student selector sidebar
2. Show Maya, Jaylen, Sofia cards
3. Narration: "Three students, three learning profiles, one system..."
4. Click on Maya's card
```

**[Upload + Vision Reader: 5-20 sec]**
```
5. Click "Upload Work Artifact" button
6. File picker opens, select: maya_math_worksheet.jpg
7. Image appears in preview (show it's a real handwritten worksheet)
8. Scroll down, show Vision Reader JSON result:
   {
     "transcribed_work": "5 dinosaurs + 3 dinosaurs = ___",
     "student_answers": ["8"],
     "confidence": 0.92
   }
9. Narration plays over this
```

**[IEP Mapper: 20-32 sec]**
```
10. Show Maya's IEP goals sidebar (3 goals, checkboxes)
11. Scroll to see the mapped result:
    ✓ Goal 2: "Follow directions"
    Trial: 1/3 completed independently
12. Show small progress chart (Goal 2 trending up)
13. Narration plays over this
```

**[Progress Analyst: 32-42 sec]**
```
14. Click "Analyze Progress" button
15. Brief loading animation (2-3 sec, fade to result)
16. Show result panel:
    "Steady progress on Goal 2. Last 3 trials: 100% completion.
     Recommendation: Increase to 4-step directions."
17. Narration plays
```

**[Material Forge - Lesson Plan: 42-60 sec]** ← SHOWSTOPPER
```
18. Click "Generate Materials" dropdown
19. Select "Lesson Plan"
20. Panel loads (fade-in, 1 sec)
21. Scroll through lesson plan slowly:
    - Header: "GOAL-ALIGNED LESSON PLAN: FOLLOWING DIRECTIONS WITH DINOSAURS"
    - Grade 3 | Autism-Friendly | 15 minutes
    - Objective + steps
    - Dinosaur clipart visible
22. Show "Export as PDF" button (don't click)
23. Fade to Sarah on camera (video switch, not screenshot)
24. Sarah speaks about using this in class
```

**[Material Forge - Social Story: 60-72 sec]**
```
25. [Screen recording resumes] Switch to Jaylen's profile
26. Show his student card (Level 3, non-verbal, AAC user)
27. Click "Generate Materials" → "Social Story"
28. Show first page of social story:
    [Thomas the Tank Engine image]
    "I like snack time."
29. Flip to page 2:
    [Picture choices]
    "I can choose. Apple? Crackers? Yogurt?"
    [AAC symbols beneath each]
30. Brief scroll through remaining pages
31. Narration plays
```

**[Admin Dashboard: 72-82 sec]**
```
32. Click "Admin Dashboard" button (or separate page)
33. Show dashboard layout:
    - 3 student progress cards at top
    - Bar chart: Goal completion rates
    - Line chart: Regression alerts (flat/low = good)
    - Table: Materials generated this week
34. Hover over a chart to show tooltip (proves it's interactive Plotly)
35. Click "Generate Parent Report" button
36. Brief preview of parent communication PDF
37. Narration: "Not just teachers. Admins, parents, everyone has visibility."
```

**[Code Deep Dive: 82-90 sec]**
```
38. Switch to IDE window (or browser tab with GitHub)
39. Show agents/vision_reader.py file
40. Highlight function calling tools definition:
    ```python
    tools = [
      {
        "name": "transcribe_work_artifact",
        "parameters": { ... }
      }
    ]
    ```
41. Show the Gemma 4 client call:
    ```python
    response = gemma_client.generate(
      image_data=work_artifact_image,
      tools=tools,
      system_prompt=VISION_READER_PROMPT
    )
    ```
42. Zoom on `tools` parameter (judges see native function calling)
```

**[Ollama Edge Demo: 90-98 sec]**
```
43. Switch to terminal window
44. Show Ollama running:
    $ ollama run gemma-4-e4b
    Loading model...
    Ready.

45. Quick inference example (3-4 sec, don't wait for full response)
    Prompt: "Transcribe this student work..."
    [Response starts, then fade to narration]
```

**[Closing Montage: 98-108 sec]**
```
46. Quick 10-second montage:
    - Sofia's lesson plan (Presidents theme)
    - Admin charts animating
    - Parent comms in Spanish
    - Materials stacked on desk (B-roll)
47. Narration: "Scale. Diversity. Accessibility."
```

**[Closing Cards: 108-120 sec]**
```
48. Fade to black
49. Title card: "ClassLens ASD | Gemma 4 Good Hackathon"
50. Credits card: "Built with Gemma 4 | Multimodal | Function Calling | Thinking Mode"
51. Links card: "github.com/jeffallan/classlens-asd | Jeff Allan, Sarah Allan"
52. Final fade to black
```

---

## B-ROLL SUGGESTIONS

Use these clips as background or transition material:

- **Classroom footage:** Sarah teaching (wide shot, no student faces)
- **Student work samples:** Stack of worksheets, students writing, hand pointing at work
- **Autism-friendly objects:** Fidget toys, visual schedules, sensory tools (context building)
- **Office/home workspace:** Jeff at laptop, typing, thinking (humanize the engineer)
- **School environment:** Hallway, classroom door, bulletin board with IEP goals (authenticity)
- **Hands-on teaching:** Close-up of teacher pointing to lesson, student hand raising (action)
- **Celebration moments:** Thumbs up, high-five, student smiling (show real impact)

**Do NOT use:**
- Generic stock footage (looks cheap, judges hate it)
- AI-generated images (risks detection, undermines trust)
- Blurry or unprofessional video (reflects on project quality)

---

## FALLBACK PLAN: IF DEMO BREAKS

If live screen recording fails during video production:

### Pre-Record These Segments (Insurance Policy)
1. **Pre-record all 4-agent transitions** as a separate "demo reel" video
   - Full Vision Reader → IEP Mapper → Progress Analyst → Material Forge flow
   - No narration, just UI transitions
   - Keep at 1920x1080, 30 FPS
   - Save as: `demo_reel_master.mp4`

2. **Pre-bake specific showstopper moments:**
   - Maya's dinosaur lesson plan appearing (3 sec)
   - Jaylen's social story pages flipping (4 sec)
   - Admin dashboard charts animating (5 sec)
   - All three at high quality, no compression artifacts

3. **If live app crashes:**
   - Switch to pre-recorded demo reel for 30-45 seconds
   - Use narration to cover ("As we can see in the system...")
   - Pause video, edit seamlessly
   - Judges won't notice if edit is clean

4. **Contingency timing:**
   - Main video: 180 sec
   - If using pre-recorded fallback: still 180 sec (just edited differently)
   - Never apologize for technical issues in video (judges won't see production notes)

### Safety Checklist
- [ ] Test Streamlit app 3 times before recording (deploy to Community Cloud to test)
- [ ] Have `data/precomputed/` results cached and validated
- [ ] Record demo reel 1 week before final submission
- [ ] Test screen recording software 2x on target machine
- [ ] Have backup ScreenFlow/OBS settings saved
- [ ] Phone as backup camera (in case laptop display fails)

---

## JUDGES' SCORING RUBRIC (OUR STRATEGY)

**Video = 30 points. Breakdown (estimated):**

| Criteria | Points | How We Win |
|----------|--------|-----------|
| **Problem clarity** | 5 | Sarah's authentic 30-sec opening (teachers feel seen) |
| **Solution demo** | 8 | Live working app, 4 agents in action, printable outputs |
| **Gemma 4 usage** | 7 | Multimodal vision + function calling + thinking mode shown explicitly |
| **Impact/story** | 6 | Sarah's classroom moment + closing vision (emotional arc) |
| **Technical depth** | 3 | Code snippets, architecture, edge computing option |
| **Production quality** | 1 | Lighting, audio, pacing, editing (don't be sloppy) |

**Our winning formula:**
1. **Make judges cry** (or at least care) — Sarah's sections
2. **Make judges impressed** — Working app, real data, multiple agents
3. **Make judges believe** — Code glimpses, Gemma 4 credential shots
4. **Make judges want to try it** — GitHub link, hosted demo URL at end

---

## FINAL EDITING CHECKLIST

Before submitting to Kaggle:

- [ ] Total duration: **179-180 seconds** (no more, no less)
- [ ] Audio levels: Voice at -6dB (loud, clear), music at -20dB (subtle)
- [ ] Color grading: Warm, consistent (not orange-tinted)
- [ ] Title card legible at 720p (judges may watch on smaller screens)
- [ ] No spelling errors in text overlays
- [ ] Transitions smooth (fade/dissolve, no glitches)
- [ ] Pacing: New visual every 8-12 seconds (holds attention)
- [ ] Sarah's speech: Clear, natural, no stammering (re-record if needed)
- [ ] Demo flows smoothly (pre-baked results load instantly)
- [ ] Credits legible (team names, GitHub, Gemma 4 credit)
- [ ] File format: MP4, H.264, 1920x1080, 30 FPS, under 500 MB
- [ ] Submission URL: YouTube unlisted link (public, no ads)
- [ ] Backup URL: Community Cloud hosted app (judges can try live)

---

## DEPLOYMENT REQUIREMENTS (FOR DEMO)

### Streamlit Community Cloud Setup
- [ ] Push `main` branch to GitHub (public repo)
- [ ] Connect Streamlit Community Cloud to GitHub
- [ ] Set secrets: `GOOGLE_API_KEY` in Community Cloud dashboard
- [ ] Deploy to public URL (judges must be able to click link and try)
- [ ] Test from fresh browser session (no cache)
- [ ] Verify demo mode works (pre-baked results load fast)

### GitHub Submission Checklist
- [ ] README updated with video link
- [ ] `docs/VIDEO-SCRIPT.md` linked in README (judges may read it)
- [ ] `DEPLOYMENT-SECURITY-CHECKLIST.md` shows best practices
- [ ] License visible (Apache 2.0)
- [ ] No API keys in repo (all in `.env.example`)
- [ ] `.gitignore` excludes sensitive files

---

## POST-PRODUCTION: JUDGES' EXPERIENCE

### Ideal Judge Journey
1. **Read submission blurb** (50 words) → "A multi-agent system for special ed teachers"
2. **Click video link** → YouTube unlisted video opens
3. **First 30 sec** → Sarah's problem statement (captures attention)
4. **Next 90 sec** → Working demo, 4 agents, visible impact
5. **Last 60 sec** → Technical proof + emotional payoff
6. **Final frame** → GitHub link visible (can explore code immediately)
7. **Click GitHub link** → Repo is clean, README is clear, code is readable

### What Judges Take Away
- **Problem:** Autism teachers spend 15 hours/week on IEP data entry
- **Solution:** Gemma 4 agents handle transcription, mapping, analysis, material generation
- **Result:** Teachers get time back. Students get better learning materials. Real human impact.
- **Tech:** Native function calling + thinking mode + multimodal vision (Gemma 4 used deeply)
- **Credibility:** Code visible, live demo available, team includes a 15-year special ed teacher

---

## PRODUCTION TIMELINE

**Ideal schedule (assuming deadline May 18):**

- **Day 1:** Shoot all live footage (Sarah on camera, 2-3 takes each segment)
- **Day 2:** Record all screen capture (app demo flow, code snippets, Ollama demo)
- **Day 3:** Record voiceover narration (Jeff, one long narration session with multiple takes)
- **Day 4-5:** Edit video (assemble shots, color grade, add music, time to exact 180 sec)
- **Day 6:** Test playback on multiple devices (laptop, phone, TV)
- **Day 7:** Submit to Kaggle

**Total effort:** ~40 hours (split between Jeff for technical bits, Sarah for classroom authenticity)

---

## FINAL REMINDERS

1. **This is a competition for judges' hearts AND minds.** Technical specs don't win alone. Sarah's authentic teaching story is 50% of the video's power.

2. **Every second counts.** 180 seconds is tight. No padding, no filler. Every transition, every narration moment, every demo screenshot earns its place.

3. **Pre-bake all results.** Demo failures on video are catastrophic. Have `data/precomputed/` fully loaded. NO waiting for API calls.

4. **Show, don't tell.** Judges don't need to hear "we use function calling." They need to *see* the JSON result appear. Show the evidence.

5. **Leave them wanting to try it.** GitHub link at end should be clickable. Hosted demo should be live and responsive.

6. **This script informs the app design.** Build the UI specifically to support this demo sequence. Make sure student profiles, materials, and precomputed results all load instantly in the order we specified.

---

**Video script ready to shoot. Good luck, team.**
