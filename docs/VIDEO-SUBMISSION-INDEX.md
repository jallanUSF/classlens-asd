# Video Submission Package — Index & Quick Reference

**Competition:** Kaggle Gemma 4 Good Hackathon | **Track:** Future of Education + Special Tech  
**Deadline:** May 18, 2026 | **Video = 30 points of 100-point score**

---

## Video Production Documents (Read in This Order)

### 1. **VIDEO-SCRIPT.md** (Primary Document)
**Purpose:** Complete 3-minute video script with full production details  
**Read if:** You're about to shoot the video or edit it  
**Includes:**
- Production notes (equipment, software, audio mix, editing specs)
- Shot list (14 shots, numbered, with timestamps and exact narration)
- B-roll suggestions
- Screen recording guide with exact clicks to make
- Timing breakdown (180 seconds, zero buffer)
- Emotional arc (problem → solution → impact → vision)
- Technical depth moments (earn judges' confidence)
- Fallback plan (if live demo fails)

**Time to read:** 25 minutes

---

### 2. **VIDEO-PRODUCTION-CHECKLIST.md** (Shoot Day Reference)
**Purpose:** Day-by-day checklist for actual video production  
**Read if:** You're in the next week before shooting  
**Includes:**
- Pre-production equipment list (camera, mic, lights, software)
- Location scouting checklist
- Materials prep (sample images, profiles, precomputed results)
- Shoot day checklists (Sarah's segments, screen recording, voiceover)
- Exact recording settings (zoom levels, file names, takes)
- Post-production editing checklist
- Audio mixing specs
- Export settings (codec, bitrate, file size)
- Submission checklist
- Backup plans (if things break)

**Time to read:** 15 minutes (reference repeatedly during production)

---

### 3. **JUDGES-PERSPECTIVE.md** (Strategy Document)
**Purpose:** Understand what judges will see, feel, and think at each moment  
**Read if:** You want to understand the strategic impact of the video  
**Includes:**
- Judge's journey step-by-step (Kaggle page → video → GitHub → live demo)
- What judges see at each video moment (0-30 sec, 30-90 sec, 90-180 sec)
- What judges think emotionally and logically
- Key moments judges will remember
- Skepticism they may have + how we address it
- Final scoring breakdown
- The winning moment (Sarah's closing)

**Time to read:** 10 minutes (read before finalizing script)

---

## Quick Navigation by Task

| Task | Document | Section |
|------|----------|---------|
| **"What should I film?"** | VIDEO-SCRIPT.md | Shot List (lines 75-432) |
| **"What equipment do I need?"** | VIDEO-PRODUCTION-CHECKLIST.md | Pre-Production (lines 1-35) |
| **"What's the exact narration?"** | VIDEO-SCRIPT.md | Shot List (all narration in quotes) |
| **"When is each video moment?"** | VIDEO-SCRIPT.md | Timing Breakdown (table, lines 516-544) |
| **"How should I edit this?"** | VIDEO-PRODUCTION-CHECKLIST.md | Post-Production / Editing (lines 263-360) |
| **"What if the demo fails?"** | VIDEO-SCRIPT.md | Fallback Plan (lines 505-515) |
| **"Why does this strategy work?"** | JUDGES-PERSPECTIVE.md | Key Moments (lines 495-515) |
| **"What's the emotional arc?"** | VIDEO-SCRIPT.md | Emotional Arc (lines 469-498) |
| **"What file format should I use?"** | VIDEO-PRODUCTION-CHECKLIST.md | Export Settings (lines 333-343) |
| **"How long is the video?"** | VIDEO-SCRIPT.md | Timing Breakdown (exactly 180 seconds) |

---

## Key Decisions (Made in Script)

### Casting
- **Sarah (on camera):** K-12 special ed teacher with 15 years experience
  - **Segments:** Opening emotional hook (30 sec) + Dinosaur lesson reaction (18 sec) + Closing vision (25 sec)
  - **Tone:** Authentic, slightly tired, hopeful, never salesy
  
- **Jeff (voiceover):** Developer/architect
  - **Segments:** All technical narration (agents, function calling, thinking mode)
  - **Tone:** Clear, confident, slightly slower pace (judges reading on-screen text)

### Demo Sequence
- **Students in order:** Maya → Jaylen → Sofia
- **Agents in order:** Vision Reader → IEP Mapper → Progress Analyst → Material Forge
- **Showstopper:** Dinosaur lesson plan for Maya (that's where Sarah on-camera reacts)
- **Inclusivity moment:** Jaylen's social story (non-verbal, AAC user)
- **Scale moment:** Admin dashboard (multiple students, multiple stakeholders)

### Technical Proof Points
1. **Function calling visible** (JSON schema on screen)
2. **Thinking mode evident** (reasoning traces in Progress Analyst)
3. **Multimodal vision proof** (handwritten worksheet → transcription)
4. **Edge computing option** (Ollama + Gemma 4E4B, 8 sec)

### Emotional Arc
- **Act 1 (Problem):** Sarah's 15-hour data entry burden (0-30 sec)
- **Act 2 (Solution):** App works, shows dinosaur lesson plan, teacher uses it in class (30-125 sec)
- **Act 3 (Impact):** "I have Tuesdays again. I have afternoons to teach." (125-180 sec)

---

## Pre-Shooting Preparation Checklist

Before you record a single frame, ensure:

- [ ] **Script locked.** No more changes to narration or timing.
- [ ] **Streamlit app deployed** to Community Cloud (not running locally).
- [ ] **Demo mode enabled** — all precomputed results cached in `data/precomputed/`.
- [ ] **Test demo 5x.** Click each button, verify results load instantly.
- [ ] **Sample images ready:** Maya (dinosaur math), Jaylen (choice board), Sofia (presidents essay).
- [ ] **Student profiles finalized** with IEP goals, interests, confidence levels.
- [ ] **Sarah's script printed** with exact narration highlighted.
- [ ] **Equipment tested:** Camera (1080p), external mic, lighting, screen recording software.
- [ ] **Classroom location scouted** (background visible, good lighting).
- [ ] **Background music sourced** (royalty-free, uplifting piano/orchestral).
- [ ] **Editing software tested** (Premiere, Final Cut, DaVinci Resolve) with sample footage.

**Total prep time:** 3-4 days before shoot day.

---

## During Production

### Day 1: Live Footage (Sarah segments)
- Record Sarah's opening emotional hook (3-4 takes, pick best)
- Record Sarah's dinosaur lesson reaction (3-4 takes)
- Record Sarah's closing vision (4-5 takes — this is critical)
- **Total time:** 2-3 hours (including setup, retakes, breaks)

### Day 2: Screen Recording (app demo)
- Record app sidebar + upload flow (5-20 sec)
- Record IEP mapper results (20-32 sec)
- Record Progress Analyst (32-42 sec)
- Record Material Forge lesson plan (42-60 sec)
- Record Jaylen social story (60-72 sec)
- Record Admin Dashboard (72-82 sec)
- Record code snippets (82-90 sec)
- Record Ollama edge demo (90-98 sec)
- **Total time:** 2-3 hours (including setup, retakes, test clicks)

### Day 3: Voiceover Narration
- Record all narration segments (Jeff)
- 3-4 takes per segment
- **Total time:** 2 hours

**Total production time: 6-8 hours across 3 days**

---

## Post-Production

### Editing (Days 4-5)
- Assemble all footage on timeline
- Sync narration to visuals
- Add transitions (fade/dissolve, 0.3 sec)
- Color grade: warm for Sarah, neutral for screen recordings
- Add background music (fade in/out, -20dB volume)
- Ensure total duration = 179-180 seconds

### QA & Export
- Watch full video 3x
- Check timing (exact 180 seconds)
- Check audio sync (no mouth movement mismatch)
- Check credits legible
- Export to MP4 (H.264, 1920x1080, 30 FPS, 8-12 Mbps)
- Test playback on 3 devices (laptop, phone, tablet)

**Total post-production time: 8-10 hours**

---

## Submission Checklist

Before clicking "Submit" on Kaggle:

- [ ] Video duration: **exactly 179-180 seconds**
- [ ] Video format: **MP4, H.264, 1920x1080, 30 FPS**
- [ ] Video uploaded to **YouTube (unlisted)**
- [ ] YouTube link **tested** (plays without errors)
- [ ] Kaggle submission includes:
  - [ ] YouTube video URL
  - [ ] GitHub link
  - [ ] Live demo URL (Streamlit Community Cloud)
- [ ] GitHub README updated with:
  - [ ] VIDEO-SCRIPT.md link
  - [ ] Live demo URL
  - [ ] Video description
- [ ] Live demo tested (loads in <5 sec, demo mode works)
- [ ] Code review (no API keys in repo, `.env.example` only)
- [ ] Submit **at least 3 days early** (May 15, not May 18)

---

## Key Success Factors

1. **Sarah's authenticity** — No acting. Real teacher, real frustration, real hope. (40% of video impact)
2. **Working demo** — Everything pre-baked. Zero wait times. App is responsive. (30% of impact)
3. **Emotional arc** — Problem → Solution → Vision. Makes judges care. (20% of impact)
4. **Technical proof** — Function calling visible. Gemma 4 capabilities obvious. (10% of impact)

**Missing any of these = you lose.**)

---

## Files Ready to Reference During Production

- [ ] `VIDEO-SCRIPT.md` — Printed or on second monitor during shoot
- [ ] `VIDEO-PRODUCTION-CHECKLIST.md` — Printed, check off items as you go
- [ ] `JUDGES-PERSPECTIVE.md` — Read before final edit to ensure emotional impact

---

## Timeline Summary

| Phase | Days | Effort | Deliverable |
|-------|------|--------|-------------|
| **Pre-Production** | 1-4 | 16 hrs | Equipment ready, script locked, demo tested 5x |
| **Shoot** | 5-7 | 8 hrs | Sarah footage, screen recordings, voiceover |
| **Edit** | 8-9 | 10 hrs | Final video, 180 seconds, H.264 MP4 |
| **QA & Submit** | 10 | 2 hrs | Kaggle submission, all links verified |
| **TOTAL** | **10 days** | **36 hours** | **Winning video ready** |

**Recommend: Start prep on May 1, submit on May 15 (3-day buffer before May 18 deadline)**

---

## Contact & Support

**If you have questions about:**
- **Narration/script:** Refer to VIDEO-SCRIPT.md or JUDGES-PERSPECTIVE.md
- **Technical specs:** Refer to VIDEO-PRODUCTION-CHECKLIST.md (Export Settings section)
- **Judge expectations:** Refer to JUDGES-PERSPECTIVE.md
- **Demo workflow:** Refer to VIDEO-SCRIPT.md (Screen Recording Guide section)

**All three documents are designed to be read independently. Cross-reference as needed.**

---

**Last Updated:** April 4, 2026  
**Status:** Ready to shoot  
**Confidence Level:** High (all variables controlled, judges' expectations mapped, emotional arc validated)

---

**Good luck. You've got this.**
