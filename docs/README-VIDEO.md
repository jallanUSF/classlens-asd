# ClassLens ASD Video Submission — Complete Package

**Date Created:** April 4, 2026  
**Status:** Ready to produce  
**Competition:** Kaggle Gemma 4 Good Hackathon (Future of Education + Special Tech)  
**Deadline:** May 18, 2026  
**Video Score:** 30 points out of 100 (most critical deliverable)

---

## What You Have

### 5 Production Documents (in `/docs/`)

1. **VIDEO-SCRIPT.md** (34 KB, 25 min read)
   - Complete 3-minute video script with 14 numbered shots
   - Exact narration text (word-for-word)
   - Shot descriptions, timing, camera directions
   - Emotional arc breakdown (problem → solution → impact)
   - Technical depth moments for judge credibility
   - Fallback plan if demo fails

2. **VIDEO-PRODUCTION-CHECKLIST.md** (16 KB, 15 min read)
   - Day-by-day production checklist
   - Equipment list (camera, mic, lights, software)
   - Pre-production, shoot day, post-production workflows
   - Audio mixing and export specs
   - Submission checklist before Kaggle upload

3. **JUDGES-PERSPECTIVE.md** (15 KB, 10 min read)
   - What judges will see at each video moment
   - What judges will think (emotional + logical)
   - Key moments judges will remember
   - Skepticism addressed
   - Scoring breakdown (30 points)

4. **APP-BUILD-FOR-VIDEO.md** (12 KB, 15 min read)
   - App architecture requirements (driven by video needs)
   - Precomputation strategy (zero-latency demo)
   - Streamlit UI structure for each video moment
   - PDF export requirements
   - Testing checklist

5. **VIDEO-SUBMISSION-INDEX.md** (10 KB, 5 min read)
   - Quick reference guide
   - Timeline summary
   - Navigation table by task
   - Key decisions documented

---

## How to Use These Documents

### If you're starting now (April 4):
1. Read **VIDEO-SCRIPT.md** (25 min) to understand the full vision
2. Read **JUDGES-PERSPECTIVE.md** (10 min) to understand judge expectations
3. Print **VIDEO-PRODUCTION-CHECKLIST.md** and tape to monitor
4. Hand **APP-BUILD-FOR-VIDEO.md** to engineering team
5. Reference **VIDEO-SUBMISSION-INDEX.md** as you go

### If you're shooting next week:
1. Review **VIDEO-SCRIPT.md** line by line (mark script with timing notes)
2. Print **VIDEO-PRODUCTION-CHECKLIST.md** (check off items as you go)
3. Have **APP-BUILD-FOR-VIDEO.md** loaded on a second screen while testing app
4. Use **VIDEO-SUBMISSION-INDEX.md** to navigate between docs

### If you're in post-production (editing):
1. Keep **VIDEO-SCRIPT.md** open (reference exact narration + timing)
2. Reference **JUDGES-PERSPECTIVE.md** (ensure emotional arc is intact)
3. Follow **VIDEO-PRODUCTION-CHECKLIST.md** (Post-Production section, lines 263-360)
4. Use **VIDEO-SUBMISSION-INDEX.md** (navigate by task)

### If you're submitting to Kaggle:
1. Review **VIDEO-SUBMISSION-INDEX.md** (Submission Checklist section)
2. Verify against **VIDEO-PRODUCTION-CHECKLIST.md** (final QA)
3. Double-check video matches **VIDEO-SCRIPT.md** (timing, narration)

---

## Key Production Facts (From Script)

### Timing
- **Total duration:** 179-180 seconds (exactly 3 minutes, zero buffer)
- **Sarah on-camera:** 73 seconds (opening 30 sec + reaction 18 sec + closing 25 sec)
- **App demo:** 70 seconds (4 agents visible)
- **Technical depth:** 13 seconds (code + Ollama)
- **Credits:** 12 seconds

### Casting
- **Sarah:** K-12 special ed teacher (15 years), on-camera narrator
- **Jeff:** Developer/architect, voiceover narrator

### Key Moments (Judges Will Remember These)
1. **0:00-0:30** — Sarah: "My Monday afternoons are just... IEP data entry"
2. **0:42-0:50** — JSON transcription appears (Gemma 4 multimodal proof)
3. **1:08-1:25** — Dinosaur lesson plan appears (app working)
4. **1:25-1:45** — Sarah on camera: "This is what changed my mind"
5. **2:35-3:00** — Sarah: "I have Tuesdays again. I have afternoons to teach."

### Technical Proof Points (Judges Will Verify These)
- **Multimodal vision:** Handwritten worksheet → JSON transcription
- **Function calling:** JSON schema visible on screen
- **Thinking mode:** Reasoning traces shown (if API exposes them)
- **Edge computing:** Ollama + Gemma 4E4B demo

---

## Production Timeline (Recommended)

| Week | Days | Task | Deliverable |
|------|------|------|-------------|
| 1 (Apr 4-10) | 1-3 | Script lock + app design | VIDEO-SCRIPT.md finalized |
| 1 | 4-7 | App build + precomputation | Demo mode working |
| 2 (Apr 11-17) | 8-9 | Production prep | Equipment ready, locations scouted |
| 2 | 10-12 | Shoot video (3 days) | All footage captured |
| 3 (Apr 18-24) | 13-16 | Edit + color grade | Video assembled, 180 sec |
| 3 | 17-18 | Audio + final export | MP4 file ready |
| 3 | 19-20 | Kaggle submission | Video live, all links verified |
| 3 | 21 | Buffer | Respond to judge questions |

**Total effort:** ~36-40 hours across 3 weeks

---

## Success Criteria

### Video Must:
- [ ] Be exactly 179-180 seconds (no shorter, no longer)
- [ ] Show Sarah authentically (not acting, real emotion)
- [ ] Demonstrate all 4 agents working (Vision, IEP, Analyst, Forge)
- [ ] Show function calling JSON on camera
- [ ] Include dinosaur lesson plan moment (showstopper)
- [ ] Include Sarah's closing vision ("I have Tuesdays again")
- [ ] Have clear, synced audio (voice at -6dB, music at -20dB)
- [ ] Be color-graded warmly (ASD-friendly, calm, welcoming)
- [ ] Include working app demo (no wait times, all instant)
- [ ] Have professional title + credits

### App Must:
- [ ] Load all demo results instantly (< 100ms per click)
- [ ] Show 3 students (Maya, Jaylen, Sofia)
- [ ] Display all 4 agent outputs
- [ ] Export lesson plans as printable PDFs
- [ ] Export social stories as printable PDFs
- [ ] Render admin dashboard with Plotly charts
- [ ] Have readable code visible on screen

### Submission Must:
- [ ] Include YouTube (unlisted) link
- [ ] Include GitHub link (public repo)
- [ ] Include Streamlit Community Cloud link (live demo)
- [ ] Be submitted by May 15 (3 days early)
- [ ] Have no API keys in code (only .env)
- [ ] Pass judges' skepticism test (they'll read code + try app)

---

## Risk Mitigation

### Risk: Live demo fails during recording
**Mitigation:** Pre-record all demo sequences as fallback; edit seamlessly

### Risk: Sarah's footage looks unprofessional
**Mitigation:** Do 4-5 takes, pick best; have backup narration (Jeff can read her words)

### Risk: Audio is bad
**Mitigation:** Record voiceover in quiet room; re-record if needed (voiceover is easy to redo)

### Risk: App crashes on camera
**Mitigation:** Pre-bake ALL results; demo mode never calls API; test 5x before recording

### Risk: Video is too long or too short
**Mitigation:** Script is timed to exact second; use stopwatch while editing

### Risk: Judges can't find live demo
**Mitigation:** Test Streamlit Community Cloud link 3x before submitting; have GitHub fallback

---

## What Judges Are Looking For (In Order of Importance)

1. **Does this solve a real teacher problem?** (Sarah answers this in 30 sec)
2. **Can the team execute?** (Working demo proves this)
3. **Is it using Gemma 4 meaningfully?** (Function calling + vision + thinking mode visible)
4. **Will this scale?** (Admin dashboard + multiple students prove this)
5. **Is the team credible?** (Sarah's expertise + code quality prove this)

---

## The Winning Formula

**40% Sarah's authenticity** + **30% Working demo** + **20% Emotional arc** + **10% Technical proof** = **WIN**

If any of these is missing, you lose. If all four are strong, you win.

---

## Files in This Directory

```
docs/
├── README-VIDEO.md ← You are here
├── VIDEO-SCRIPT.md (primary, 34 KB)
├── VIDEO-PRODUCTION-CHECKLIST.md (shoot reference, 16 KB)
├── JUDGES-PERSPECTIVE.md (strategy, 15 KB)
├── APP-BUILD-FOR-VIDEO.md (engineering, 12 KB)
└── VIDEO-SUBMISSION-INDEX.md (navigation, 10 KB)
```

---

## Next Steps

### Immediately (April 4):
- [ ] Print VIDEO-SCRIPT.md + VIDEO-PRODUCTION-CHECKLIST.md
- [ ] Share APP-BUILD-FOR-VIDEO.md with engineering team
- [ ] Reserve shoot dates (May 5-7 recommended)
- [ ] Book classroom location for Sarah footage
- [ ] Procure equipment (camera, mic, lights)

### By April 10:
- [ ] App design finalized (based on APP-BUILD-FOR-VIDEO.md)
- [ ] Sample student work artifacts collected (real handwritten work)
- [ ] Student profiles finalized (IEP goals, interests, learning levels)
- [ ] Precomputation started (generate demo results)

### By April 20:
- [ ] All shooting complete
- [ ] Voiceover recorded
- [ ] Footage organized + backed up

### By April 25:
- [ ] Video edited to 180 seconds
- [ ] Color graded + audio mixed
- [ ] Exported to MP4 (H.264, 1920x1080, 30 FPS)

### By April 28:
- [ ] Video uploaded to YouTube (unlisted)
- [ ] Live demo tested on Streamlit Community Cloud
- [ ] All links verified

### By May 15:
- [ ] Kaggle submission complete
- [ ] All links working
- [ ] Buffer time before May 18 deadline

---

## Questions?

**"What should I film?"** → Read VIDEO-SCRIPT.md (Shot List)

**"How do I film it?"** → Read VIDEO-PRODUCTION-CHECKLIST.md

**"Why does this strategy work?"** → Read JUDGES-PERSPECTIVE.md

**"How should I build the app?"** → Read APP-BUILD-FOR-VIDEO.md

**"What's the timeline?"** → Read VIDEO-SUBMISSION-INDEX.md (Timeline Summary)

---

## Final Reminder

**This is 30 points out of 100.** You need this video to win the hackathon.

Every second counts. Every moment is strategic. Every choice matters.

The script is locked. The app architecture is defined. The judge expectations are mapped.

You have everything you need to execute. Now go build something great.

---

**Last updated: April 4, 2026**  
**Ready to shoot: Yes**  
**Confidence: High**

**Good luck.**
