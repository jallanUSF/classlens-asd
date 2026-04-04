# Sarah's Original Vision

> A lot of autistic kids are hyper focused on one thing: for example, dinosaurs or robots or space or presidents or whatever so what if there was a program that you could input the child's interest say it's dinosaurs and input the learning target say writing their name or simple addition, etc., and it comes up with things (lesson plans, activities, work sheets, printable work mats etc) that are tailored to that skill that also incorporate the thematic dinosaur aspect. (Or space, or cars or whatever). Does that make sense? So rather than me having to search the internet and tons of sites like TPT, Pinterest etc. it just does it for me. Because it's not so bad when you just have one kid... but trying to tailor a lesson to 8 kids who each have their own different hyper focus is a lot of work.

---

## How This Idea Became ClassLens ASD

Sarah's insight above is the foundation of the entire project. Here's how it maps to what we're building:

**Her core problem:** Personalizing materials for 8 kids with 8 different hyperfocuses is unsustainable by hand.

**What we added on top:**
- The same teacher who creates those materials also has to track IEP progress data by hand (tally marks, trial counts, percentages) — that's the other half of the time drain.
- AI can now read photos of student work (handwriting OCR), which means the data collection step can be partially automated too.

**So ClassLens ASD does both:**
1. **Automates the data grind** — Photo of student work goes in, IEP-aligned progress data comes out (Agents 1-3: Vision Reader, IEP Mapper, Progress Analyst)
2. **Generates the personalized materials Sarah described** — Dinosaur-themed social stories for Maya, train-themed visual schedules for Jaylen, each matched to the student's actual IEP goals and communication level (Agent 4: Material Forge)

Sarah's original idea IS the Material Forge agent. We just wrapped it in a full data pipeline so the personalized materials are also *informed by the student's actual progress data* — not just their interests, but what they need to work on next based on their trends.

---

## Open Questions Only Sarah Can Answer

These are the things that require her domain expertise as a practicing teacher of ASD students. No amount of research or code can substitute for this knowledge.

### Student Profiles
- [ ] What does a realistic classroom look like? (How many students, what range of support levels, what ages?)
- [ ] What are 3-5 believable fictional student profiles with proper IEP goals? (See teacher-playbook.md Section 2.1 for the full template)
- [ ] What interests do her real students tend to have? (We need the specific ones — "Thomas the Tank Engine" not just "trains")
- [ ] What does a realistic sensory profile look like for each support level?

### Work Artifacts
- [ ] What kinds of worksheets/tally sheets does she actually use day-to-day?
- [ ] Can she create or photograph 5-10 sample artifacts? (Messy is better — real classroom conditions)
- [ ] What does a completed visual schedule board actually look like?
- [ ] What does a behavior tally sheet look like mid-day vs end-of-day?

### "Gold Standard" Outputs
- [ ] What does a progress note look like that she'd actually submit to an IEP team?
- [ ] What does a social story look like that she'd actually use with a student?
- [ ] What would she actually send home to a parent?
- [ ] What kind of alert would actually change tomorrow's instruction?

### Dashboard / UX
- [ ] What would a "useful at a glance" end-of-day view look like? (Sketch on paper)
- [ ] What information does she need FIRST when she sits down after school?
- [ ] What's noise vs. signal in progress data?

### Video
- [ ] Can she describe the IEP data collection grind in 30 seconds?
- [ ] Can she introduce a fictional student naturally on camera?
- [ ] Can she react genuinely to a ClassLens output on camera?

---

## Sarah's Second Input (April 4, 2026)

> Another idea (and this might be more feasible) is a program you can input each child's IEP goal and get lessons and a data tracker that is specific to that goal. So sometimes an IEP goal would be like "Sam will use two to three word phrases or sentences correctly 90% of the time in response to a direct question" then you could get some ideas for lessons and activities that help to build up to that goal, along with data tracking sheets. Admin/managers eat up fancy reports and data.

### What This Tells Us

Sarah keeps circling back to the same core need across both messages: **IEP goal in → lesson plans and activities out.** That's her #1 pain point. The interest-based personalization (message 1) and the goal-based lesson generation (message 2) are two sides of the same coin — she wants materials that are both goal-aligned AND student-personalized.

### Three New Output Types Identified

1. **Goal-aligned lesson plans and activities** — Given an IEP goal like "Sam will use 2-3 word phrases 90% of the time," generate scaffolded lesson ideas, activities, and practice worksheets that build toward mastery. This is BROADER than social stories — it's instructional planning.

2. **Printable data tracking sheets** — Per-goal tracking sheets designed to be printed and carried on a clipboard during instruction. Not a screen dashboard — a physical tool for the classroom.

3. **Admin/IEP team reports** — Polished, professional reports with charts and trend data. Second audience beyond the teacher: administrators and IEP team members who "eat up fancy reports and data."

### Impact on Material Forge (Agent 4)

Current outputs: social stories, visual schedules, first-then boards, parent comms.

**Add:**
- Lesson plan / activity suggestions (per IEP goal, incorporating student interests)
- Printable data tracking sheets (per goal, clipboard-ready format)
- Admin progress reports (polished PDF/printable with charts, professional language)

### Impact on Competition Strategy

The admin reports angle is actually a HUGE competition differentiator. It shows ClassLens serves multiple stakeholders: the teacher (daily workflow), the student (personalized materials), AND the administration (compliance reporting). That's a stronger impact story than a teacher-only tool.

The IEP goal example Sarah gave ("Sam will use two to three word phrases or sentences correctly 90% of the time in response to a direct question") is PERFECT for the demo — it's specific, measurable, and easy for judges to understand even without special education knowledge.

---

## Status

**Last updated:** April 4, 2026
**Project deadline:** May 18, 2026
**Week 1 starts:** April 5, 2026
**Sarah's items needed by:** See Sarah-Plan.md for weekly breakdown
