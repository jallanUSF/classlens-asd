# ClassLens ASD Video Production Checklist
**Quick Reference for Shoot Day**

---

## PRE-PRODUCTION (1 week before shoot)

### Equipment & Software
- [ ] Camera/phone tested (1080p minimum)
- [ ] External USB mic purchased + tested
- [ ] Lighting setup (soft key + fill light ready)
- [ ] Screen recording software installed (OBS, Camtasia, ScreenFlow)
- [ ] Video editing software ready (Premiere, Final Cut, DaVinci Resolve)
- [ ] Audio editing software ready (Audacity, Logic)
- [ ] Streamlit app deployed to Community Cloud (working URL)
- [ ] Demo mode enabled (all precomputed results cached)
- [ ] GitHub repo public + README updated

### Locations Scouted
- [ ] Classroom backdrop for Sarah segments (quiet, well-lit)
- [ ] Home office backdrop for Jeff segments (professional, uncluttered)
- [ ] Demo recording environment (laptop on desk, second monitor if possible)

### Materials Prepared
- [ ] Sample student work artifacts ready:
  - `maya_math_worksheet.jpg` (handwritten dinosaur math)
  - `jaylen_choice_board.jpg` (picture choice board)
  - `sofia_presidents_essay.jpg` (handwritten essay)
- [ ] Student profile JSON files validated
- [ ] IEP goal data finalized
- [ ] Precomputed results generated and cached in `data/precomputed/`
- [ ] Plotly dashboard tested (charts animate smoothly)

### Script & Timing
- [ ] VIDEO-SCRIPT.md printed (one copy for Sarah, one for Jeff)
- [ ] Exact narration text highlighted
- [ ] Timing notes reviewed (30 sec opening, 90 sec demo, 60 sec closing)
- [ ] Shot list printed with timestamps
- [ ] B-roll suggestions list prepared

---

## SHOOT DAY (Day 1): LIVE FOOTAGE

### Sarah's Segments (Classroom — morning shoot)

**Segment 1: Opening Problem Statement (30 sec)**
- [ ] Lighting set up (natural light or 2-light setup)
- [ ] Sarah seated, chest-up framing
- [ ] Test audio (external mic, no echo)
- [ ] Sarah reads script 3-4 times (natural delivery, not robotic)
- [ ] Record 5-6 full takes
- [ ] Best take should feel conversational + authentic
- [ ] Save as: `SARAH_OPENING_TAKE1.mov`, `TAKE2.mov`, etc.

**Segment 2: Dinosaur Lesson Plan Reaction (18 sec)**
- [ ] Different shot angle (sitting, maybe at a table with lesson plan printed)
- [ ] "This is what changed my mind..." narration
- [ ] Show printed dinosaur lesson plan (hold it, point to it)
- [ ] Reaction should feel genuine (not overacted)
- [ ] Record 4-5 takes
- [ ] Save as: `SARAH_REACTION_DINOSAUR_TAKE1.mov`, etc.

**Segment 3: Closing Vision (25 sec)**
- [ ] Back to original framing (chest-up, eye contact)
- [ ] "I have Tuesdays again..." narration
- [ ] Speak slowly, pauses between thoughts
- [ ] Emotion: hopeful, grounded, not sales-pitchy
- [ ] Record 4-5 takes (this is critical)
- [ ] Save as: `SARAH_CLOSING_TAKE1.mov`, etc.

### Notes on Sarah's Shoots
- Avoid harsh shadows on face
- Encourage natural pauses (don't rush delivery)
- Have water available
- Review playback after each segment
- If Sarah seems tense, take a 10-min break
- Best takes usually come in takes 3-5, not take 1

---

## SHOOT DAY (Day 2): SCREEN RECORDING

### Setup (Before Recording)
- [ ] Streamlit app running locally OR on Community Cloud
- [ ] Browser zoomed to 125% (readable text)
- [ ] Entire Streamlit window visible (no taskbar)
- [ ] Second monitor available (not mirrored)
- [ ] Screen resolution: 1920x1080
- [ ] Frame rate: 30 FPS
- [ ] Demo mode VERIFIED (all precomputed results ready)
- [ ] Test clicks 3x (do they load fast?)
- [ ] Screenshot each test click (verify results load)

### Recording Sequence (Follow shot list exactly)

**[0-5 sec] Student Selector Sidebar**
- [ ] App opens to sidebar
- [ ] Maya, Jaylen, Sofia cards visible
- [ ] Record 1x (this is quick)

**[5-20 sec] Upload & Vision Reader**
- [ ] Click "Upload Work Artifact"
- [ ] Select `maya_math_worksheet.jpg`
- [ ] Image displays (handwritten worksheet visible)
- [ ] JSON result appears (transcription visible)
- [ ] Record 1x (slow down click speed for visibility)

**[20-32 sec] IEP Mapper Goal Detection**
- [ ] Maya's IEP goals visible in sidebar
- [ ] Click to mapped results
- [ ] Goal 2 marked with checkmark
- [ ] Trial data shows: 1/3 completed
- [ ] Progress chart visible
- [ ] Record 1x

**[32-42 sec] Progress Analyst**
- [ ] Click "Analyze Progress"
- [ ] Wait for result (should be instant due to precompute)
- [ ] Result panel shows recommendation
- [ ] Record 1x

**[42-60 sec] Material Forge Lesson Plan** ← CRITICAL
- [ ] Click "Generate Materials" → "Lesson Plan"
- [ ] Lesson plan loads (fade-in should be smooth)
- [ ] Scroll through content slowly (judges read it)
- [ ] Dinosaur clipart visible
- [ ] Show "Export as PDF" button
- [ ] Record 2x (take best)

**[60-72 sec] Social Story for Jaylen**
- [ ] Switch to Jaylen's profile
- [ ] Show "Generate Materials" → "Social Story"
- [ ] Flip through pages 1-3
- [ ] AAC symbols visible
- [ ] Record 1x

**[72-82 sec] Admin Dashboard**
- [ ] Click to Admin Dashboard
- [ ] Show 3 student cards
- [ ] Show bar chart + line chart
- [ ] Show materials table
- [ ] Hover over chart (prove it's interactive Plotly)
- [ ] Record 1x

**[82-90 sec] Code Deep Dive**
- [ ] Switch to IDE (VS Code, GitHub, etc.)
- [ ] Show `agents/vision_reader.py`
- [ ] Highlight tools definition (15 sec)
- [ ] Highlight Gemma client call (5 sec)
- [ ] Record 1x (zoom on key lines)

**[90-98 sec] Ollama Edge Demo**
- [ ] Switch to terminal
- [ ] Show `ollama run gemma-4-e4b`
- [ ] Quick inference (3-4 sec, don't wait for full response)
- [ ] Record 1x (even if response is incomplete, fade before it finishes)

### Screen Recording Notes
- Minimize distractions (close Slack, email, other apps)
- Move mouse out of view when narration is over
- Don't click unnecessarily (judges notice nervous clicking)
- If something breaks, stop, reload, restart from last checkpoint
- Record full takes even if one section feels off (you may salvage it in edit)
- Save all footage immediately to external drive (backup plan)

**Save files as:**
- `SCREENDEMO_APP_0-5sec.mov`
- `SCREENDEMO_UPLOAD_5-20sec.mov`
- `SCREENDEMO_MAPGOALS_20-32sec.mov`
- etc. (one file per major segment)

---

## SHOOT DAY (Day 3): VOICEOVER NARRATION

### Setup
- [ ] Quiet room (minimal background noise)
- [ ] External USB mic plugged in + tested
- [ ] Audacity or Logic open
- [ ] VIDEO-SCRIPT.md narration text copied into text editor (for reference)
- [ ] Headphones available (monitor audio)
- [ ] Water bottle ready (dry throat kills takes)

### Recording Narration (In Order)

**Jeff's Narration Segments:**
1. (5 sec) "ClassLens ASD is a multi-agent system..."
2. (12 sec) "Vision Reader is a Gemma 4 multimodal agent..."
3. (12 sec) "IEP Mapper uses function calling to match..."
4. (10 sec) "Progress Analyst uses Gemma 4's thinking mode..."
5. (18 sec) "This is what changed my mind about AI..." (Sarah on camera, but could be voiced by Jeff if needed)
6. (12 sec) "Jaylen is non-verbal and uses AAC..."
7. (10 sec) "This isn't just for teachers. Administrators see..."
8. (8 sec) "This works with Gemma 4's native function calling..."
9. (5 sec) "The Progress Analyst uses Gemma 4's extended thinking mode..."
10. (8 sec) "We also built an offline version using Ollama..."
11. (10 sec) Demo montage narration: "Three students. Multiple learning profiles..."

### Recording Best Practices
- Record each segment separately (easier to re-do)
- Do 3-4 takes per segment
- Speak clearly, pace yourself (not too fast)
- Slight pause before/after each narration block (for editing)
- Watch the corresponding screen footage while narrating (helps with pacing)
- Avoid "umm," "uh," filler words (edit them out)
- Reference TEXT on screen when narrating (e.g., "Notice the JSON here...")

**Save files as:**
- `VO_01_multiagentagent_TAKE1.wav`
- `VO_01_multiagentagent_TAKE2.wav`
- `VO_02_visionreader_TAKE1.wav`
- etc.

---

## POST-PRODUCTION (Days 4-5): EDITING

### Video Editing Software Setup
- [ ] Video editing software open (Premiere Pro, Final Cut, DaVinci Resolve)
- [ ] New project: 1920x1080, 30 FPS, H.264 codec
- [ ] Import all screen recordings
- [ ] Import all live footage (Sarah segments)
- [ ] Import all voiceover narration
- [ ] Import background music (royalty-free piano/orchestral)
- [ ] Timeline ready

### Assembly (Follow shot list)

**[0-30 sec] Opening: Sarah Emotional Hook**
- [ ] Place Sarah opening segment on timeline
- [ ] Trim to exactly 30 sec
- [ ] Add fade-in (0.5 sec)
- [ ] Add fade-out (0.5 sec)
- [ ] Check audio: voice at -6dB (loud), clear

**[30-50 sec] Student Selector & Upload**
- [ ] Place screen recording 1 (student sidebar)
- [ ] Place screen recording 2 (upload & transcription)
- [ ] Trim combined to 20 sec
- [ ] Add Jeff's voiceover (narration 1 & 2)
- [ ] Sync speech with visual moments (e.g., "Vision Reader" spoken when Gemma thinking, "transcribes" when JSON appears)
- [ ] Add subtle background music (fade in, stay low)

**[50-62 sec] IEP Mapper & Progress Analyst**
- [ ] Place screen recordings 3 & 4
- [ ] Trim to 12 sec total
- [ ] Add narration 3 (IEP Mapper explanation)
- [ ] Sync: "maps transcribed work" → show goal mapping on screen
- [ ] Add subtle sound effect (optional): soft "whoosh" when JSON appears

**[62-102 sec] Material Forge - THE SHOWSTOPPER**
- [ ] Place screen recording 5 (lesson plan generation)
- [ ] Slow down scrolling (judges need time to read)
- [ ] Place it: first 18 sec
- [ ] Add narration 5 (Jeff intro)
- [ ] Then CUT TO: Sarah on camera (video transition, 0.3 sec dissolve)
- [ ] Sarah speaks her dinosaur lesson reaction (18 sec of her video)
- [ ] Make sure her face is prominent (zoom in slightly if needed)
- [ ] Add color grade: warm, welcoming
- [ ] Sync: lesson plan visible on left side while Sarah speaks (picture-in-picture optional, but not recommended — let her story shine)

**[102-125 sec] Social Story & Admin Dashboard**
- [ ] Place screen recording 6 (Jaylen social story)
- [ ] Trim to 12 sec
- [ ] Add narration 6
- [ ] Place screen recording 7 (admin dashboard)
- [ ] Trim to 10 sec
- [ ] Add narration 7
- [ ] Smooth transitions between segments

**[125-133 sec] Technical Depth**
- [ ] Place screen recording 8 (code deep dive)
- [ ] Trim to 8 sec
- [ ] Add narration 8
- [ ] Zoom on important lines (make text larger)
- [ ] Color highlight code syntax (optional, makes it pop)

**[133-150 sec] Technical + Edge Demo + Montage**
- [ ] Place screen recording 9 (thinking mode reasoning, if available)
- [ ] Trim to 5 sec
- [ ] Place screen recording 10 (Ollama demo)
- [ ] Trim to 8 sec
- [ ] Place rapid-fire B-roll montage (Sofia lesson plan, charts, materials)
- [ ] Trim to 10 sec
- [ ] Add narration 11 (montage voiceover)
- [ ] Speed up transitions (every 1-2 sec, new visual)

**[150-175 sec] Closing: Sarah's Vision**
- [ ] Place Sarah closing segment (25 sec video)
- [ ] Trim to exactly 25 sec
- [ ] NO narration (Sarah speaks directly to camera)
- [ ] Add warm, uplifting background music (fade in at start, fade out at end)
- [ ] Color grade: warm, sincere, hopeful
- [ ] Close-up zoom on her eyes (subtle zoom over 15 sec, not jarring)

**[175-180 sec] Credits**
- [ ] Black fade (1 sec)
- [ ] Title card: "ClassLens ASD | Gemma 4 Good Hackathon" (3 sec)
- [ ] Next card: "Built with Gemma 4: Multimodal | Function Calling | Thinking Mode" (3 sec)
- [ ] Next card: "github.com/jeffallan/classlens-asd | Jeff Allan, Sarah Allan" (3 sec)
- [ ] Final fade to black (2 sec)
- [ ] Add uplifting orchestral sting (matches title cards)

### Audio Mixing
- [ ] All voiceovers normalized to -6dB (consistent level)
- [ ] Background music: -20dB (barely audible under voice)
- [ ] Sound effects (optional): -15dB (subtle, no distraction)
- [ ] No abrupt silence (use crossfades, always ~0.5 sec transition)
- [ ] Check for pops, clicks, hum (remove with EQ)
- [ ] Final mix: export at -2dB (headroom, prevents clipping)

### Color Grading
- [ ] All Sarah footage: warm color temp (approx +200K), lifted blacks (friendly feel)
- [ ] All screen recordings: neutral, crisp contrast (readability)
- [ ] Opening fade: gradual, not harsh
- [ ] Transitions: dissolve (0.3 sec), never cut
- [ ] Credits: high contrast (legible on any screen)

### Export Settings
- [ ] Codec: H.264
- [ ] Resolution: 1920x1080
- [ ] Frame rate: 30 FPS
- [ ] Bitrate: 8-12 Mbps (high quality, under 500 MB)
- [ ] Audio: AAC stereo, 128 kbps
- [ ] Format: MP4
- [ ] File size target: 300-400 MB
- [ ] Save as: `ClassLens_ASD_Video_FINAL.mp4`

### QA Before Upload
- [ ] Watch video end-to-end (full screen, no distractions)
- [ ] Check timing: should be exactly 179-180 sec
- [ ] Check audio sync: voiceovers match on-screen text
- [ ] Check visuals: no pixelation, blur, or color banding
- [ ] Check credits: legible (test on phone screen too)
- [ ] Check for typos in overlay text (proofread 2x)
- [ ] Listen for pops, clicks, audio glitches
- [ ] Verify background music never overpowers voice
- [ ] Check that demo transitions are smooth (no stutters)
- [ ] Final check: Play on TV (larger screen catches issues)

---

## SUBMISSION CHECKLIST

### Before Upload to Kaggle
- [ ] Video file tested on YouTube (unlisted link)
- [ ] Play on 3 devices: laptop, phone, tablet (buffer/playback quality OK?)
- [ ] Video title: "ClassLens ASD — Gemma 4 Good Hackathon | Multi-Agent IEP Intelligence"
- [ ] Video description includes:
  - GitHub link
  - Live demo URL (Streamlit Community Cloud)
  - Problem statement (1-2 sentences)
  - Solution overview (1-2 sentences)
  - Tech stack: Gemma 4, Streamlit, Plotly
- [ ] YouTube visibility: UNLISTED (not private, not public)
- [ ] Get shareable link: `youtube.com/watch?v=...`
- [ ] Add link to GitHub README (`docs/VIDEO-SCRIPT.md`)
- [ ] Submit to Kaggle before deadline (May 18, 2026)

### After Submission
- [ ] Test live demo URL (judges will click it)
- [ ] Verify Streamlit app loads in <5 sec
- [ ] Verify demo mode works (no API calls)
- [ ] Check that all materials can be generated + exported
- [ ] Verify GitHub repo is public + README is clear
- [ ] Monitor Kaggle for comments (respond to judge questions)

---

## BACKUP PLAN (If Something Goes Wrong)

### If Live Demo Fails During Recording
- [ ] Have `demo_reel_master.mp4` pre-recorded and ready
- [ ] Cut it into video seamlessly (using same color grading)
- [ ] Judges won't know it's pre-recorded if edit is clean

### If Sarah's Footage Breaks (Camera Dies, Audio Bad)
- [ ] Use your 3-4 takes and choose best (you should have multiple)
- [ ] If all Sarah footage is lost: have Jeff read her narration (not ideal, but workable)
- [ ] Salvage as much as possible; don't miss deadline

### If Voiceover Audio is Bad
- [ ] Re-record immediately (don't wait)
- [ ] Voiceover is re-recordable; don't submit bad audio

### If Editing Software Crashes
- [ ] Save project every 15 minutes (auto-save enabled)
- [ ] Have project backed up to cloud (Google Drive, Dropbox)
- [ ] Switch to DaVinci Resolve (free, often more stable than Premiere)

---

## POST-SUBMISSION: JUDGE EXPERIENCE

### Judges Will Watch In This Order
1. Read submission blurb (find your video link)
2. Click YouTube link (video must load quickly)
3. Watch first 30 sec (most critical — Sarah's story)
4. If interested, watch remaining 150 sec
5. Click GitHub link (check if code is readable)
6. Click live demo URL (try app themselves)
7. Read code (especially function calling patterns)

### What Judges Are Looking For in Video
- Problem clarity (do they understand teacher pain?)
- Solution feasibility (does demo work?)
- Gemma 4 depth (is it real integration, not smoke and mirrors?)
- Impact (can they see this helping real classrooms?)
- Production quality (does it feel professional?)

### Your Advantage
- Sarah's 15 years of teaching experience (credibility)
- Real student work + real IEP goals (authenticity)
- Working multi-agent system (not vaporware)
- Printable materials (teachers can actually use outputs)
- Code visibility (judges can verify function calling)

---

**Timeline: Shoot Days 1-3, Edit Days 4-5, Submit by May 15 (3 days early buffer).**

**Good luck!**
