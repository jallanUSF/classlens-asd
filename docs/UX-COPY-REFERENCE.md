# ClassLens ASD — UX Copy Reference

Complete reference of all user-facing text for the ClassLens ASD Streamlit application. Copy is organized by screen/feature and ready for direct integration into Python/Streamlit code.

---

## Design Principles

- **Concrete vocabulary**: "student work" not "artifacts"; "uploaded photo" not "asset"
- **Short sentences**: Maximum 15 words per line
- **Active voice**: "Upload a photo" not "A photo should be uploaded"
- **Warm but professional**: Acknowledge effort, celebrate progress genuinely
- **No jargon**: Avoid "inference," "multimodal," "token," "confidence score"
- **Predictable structure**: Consistent button placement, calm colors, no surprises

---

## App Header & Navigation

### Main Page Title
```python
st.title("ClassLens ASD")
st.markdown("**Multimodal IEP Intelligence for Autistic Learners**")
```

### Tagline (below title)
```python
"Transform student work photos into IEP progress."
```

### Demo Mode Banner (if active)
```python
st.info(
    "🎯 Demo Mode Active — Using sample data for quick preview. "
    "Upload your own photos to see real results."
)
```

---

## Sidebar Navigation

### Student Selector

#### Section Header
```python
"**Select a Student**"
```

#### Student Button (example: Maya)
```python
"Maya (Grade 3) — Dinosaurs"
```

#### Student Button (example: Jaylen)
```python
"Jaylen (Grade 1) — Non-verbal / AAC"
```

#### Student Button (example: Sofia)
```python
"Sofia (Grade 5) — US Presidents"
```

#### Sidebar Helptext
```python
"Your student roster. Click to view their profile and recent work."
```

### Navigation Tabs (below student selector)
```python
tabs = ["📸 Upload", "📊 Dashboard", "🎯 Goals", "📝 Materials"]
```

#### Tab Labels
```python
"📸 Upload Work"          # Photo upload interface
"📊 Progress Dashboard"   # Trend charts and goal status
"🎯 IEP Goals"           # Goal details and history
"📝 Generated Materials" # Lesson plans, social stories, reports
```

---

## Tab 1: Upload Work

### Page Title
```python
st.title("Upload Student Work")
```

### Subtitle
```python
"Help us understand what [Student Name] can do."
```

### Work Type Selection

#### Section Header
```python
"What type of work are you uploading?"
```

#### Work Type Options (radio buttons)
```python
work_type_options = [
    ("Math Worksheet — numbers, problems solved", "math_worksheet"),
    ("Behavior Tally — marks for daily tracking", "behavior_tally"),
    ("Task Checklist — steps completed or pending", "task_checklist"),
    ("Writing Sample — essay, paragraph, story", "writing_sample"),
    ("PECS/AAC Log — communication attempts", "communication_log"),
    ("Visual Schedule — items checked off", "visual_schedule"),
    ("Other — describe what you see", "other"),
]
```

#### Work Type Helptext (shown when selected)
```python
helptext_map = {
    "math_worksheet": "Upload a photo of the worksheet. We'll count correct/incorrect/skipped.",
    "behavior_tally": "Upload tally marks (days, tallies, behaviors). We'll calculate averages.",
    "task_checklist": "Upload a checklist with items checked or unchecked. We'll count completion.",
    "writing_sample": "Upload handwritten or typed writing. We'll analyze spelling and ideas.",
    "communication_log": "Upload a log of communication attempts (AAC, gestures, words). We'll track success.",
    "visual_schedule": "Upload a schedule checklist. We'll see what's done and what's pending.",
    "other": "Describe what the photo shows. We'll do our best to understand.",
}
```

### Photo Upload

#### Upload Button Label (file uploader)
```python
"📸 Choose a photo of student work"
```

#### File Upload Helptext
```python
"JPG, PNG, or PDF. Max 10 MB. Clear, well-lit photos work best."
```

#### Drag-and-Drop Area (Streamlit default)
```python
# Streamlit renders this automatically; no custom text needed
```

### Date Selection

#### Section Header
```python
"When did this work happen?"
```

#### Date Picker Label
```python
"Date of work:"
```

#### Optional: Context Notes

#### Section Header
```python
"Anything we should know? (Optional)"
```

#### Text Area Placeholder
```python
"Examples: 'student was tired', 'first attempt at this', 'peer helped with setup'"
```

#### Text Area Helptext
```python
"Context helps us understand performance better. Keep it brief."
```

### Action Buttons

#### Primary Button (Submit Work)
```python
st.button("🚀 Upload & Analyze", key="upload_button")
```

#### Secondary Button (Load Demo)
```python
st.button("👁️ Try Demo Instead", key="demo_button")
```

#### Button Helptext (below buttons)
```python
"Analysis takes 30–60 seconds. Demo loads instantly."
```

---

## Upload States

### Before Upload (Empty State)

#### Hero Text
```python
st.markdown(
    """
    ### No work uploaded yet

    **Here's how ClassLens helps:**
    1. You upload a photo of student work
    2. We read what the student wrote or did
    3. We match the work to IEP goals
    4. We track progress over time
    5. We create lesson plans and parent letters
    """
)
```

#### Quick Start CTA
```python
"Ready? Click '📸 Upload Work' above."
```

### Uploading / Processing

#### Loading Message
```python
st.spinner("🔍 Analyzing student work...")
```

#### Detailed Progress (if multi-step)
```python
progress_messages = [
    "📸 Reading the photo…",
    "📝 Transcribing what I see…",
    "🎯 Matching to IEP goals…",
    "📊 Detecting progress trends…",
    "✅ Done!",
]
```

#### Estimated Wait Time
```python
"This takes about 30–60 seconds. Feel free to get coffee."
```

### Processing Error States

#### Generic API Error
```python
st.error(
    "❌ Oops! Something went wrong while analyzing.\n\n"
    "Try again in a moment, or contact support if this keeps happening."
)
```

#### File Upload Error (too large)
```python
st.error(
    "❌ Photo is too large (max 10 MB).\n\n"
    "Try a different photo or resize this one."
)
```

#### File Upload Error (wrong format)
```python
st.error(
    "❌ We need a JPG, PNG, or PDF.\n\n"
    "Check your file type and try again."
)
```

#### API Rate Limit
```python
st.warning(
    "⏳ We're processing a lot of uploads right now.\n\n"
    "Please wait a moment and try again."
)
```

#### Poor Image Quality
```python
st.warning(
    "📸 This photo is blurry or too dark.\n\n"
    "Try a clearer, well-lit photo for better results."
)
```

---

## Tab 2: Vision Reader Results

### Page Title
```python
st.title("What I See")
```

### Subtitle
```python
f"Analysis of {work_type} from {date}"
```

### Results Section Header
```python
"Here's what the student wrote, did, or communicated:"
```

### Vision Reader Output (examples by work type)

#### Math Worksheet Result
```python
result_text = """
**10 Problems Analyzed**

✓ Correct: 7 (70%)
✗ Incorrect: 2 (20%)
⊘ Skipped: 1 (10%)

**Details:**
- Problem #4: Skipped (no answer)
- Problem #7: Wrong (wrote 8 instead of 12)
- All other answers correct

**Confidence:** High (clear handwriting, standard format)
"""
```

#### Behavior Tally Result
```python
result_text = """
**5 Days Tracked**

**Greets Peer (per day)**
- Monday: 3
- Tuesday: 4
- Wednesday: 2 (fire drill)
- Thursday: 5
- Friday: 6

**Daily Average:** 4.0 greetings/day
**Trend:** Improving (especially Friday)

**Confidence:** High (clear tally marks)
"""
```

#### Task Checklist Result
```python
result_text = """
**7 Steps Tracked**

✓ Completed: 5 steps (71%)
⊘ Pending: 2 steps (29%)

**Done:**
1. Hands-on sensory bin ✓
2. Morning snack ✓
3. AAC warm-up ✓
4. Visual schedule review ✓
6. Work task ✓

**Not yet:**
5. Transition song
7. Clean-up

**Confidence:** High (clear checkmarks)
"""
```

#### Writing Sample Result
```python
result_text = """
**Writing Analyzed**

**Full Text (as written):**
"George Washington was the first president. He lived in Virginia.
The Constitution was creaded in 1787. Washinton was an army leader before."

**Statistics:**
- Total words: 38
- Sentences: 4
- Spelling errors: 2 (creaded, Washinton)
- Original spelling preserved ✓

**Writing Style:**
- All facts, no opinions
- Simple sentence structure
- Clear focus: Presidents

**Confidence:** High
"""
```

#### Communication Log Result
```python
result_text = """
**5 Communication Attempts**

**Successful Attempts: 4/5 (80%)**

✓ 9:00 AM — "Train" (AAC device)
✓ 10:15 AM — "Water" (picture + gesture)
✓ 11:00 AM — "Break" (picture card)
✓ 12:30 PM — "Snack" (AAC device)
✗ 1:45 PM — "More" (gesture only, prompted)

**AAC Device Use:** 2/5 (40%, truly independent)
**All Methods Combined:** 4/5 (80%)

**Trend:** Increasing AAC device use
**Confidence:** High
"""
```

### Transcription Detail View (collapsible)

#### Collapsible Header
```python
st.markdown("**View Raw Transcription**")
```

#### Content (inside collapsible)
```python
# Full transcribed text for teacher review/editing
```

### Action Buttons (below results)

#### Edit/Correct Button
```python
st.button("✏️ Correct Transcription", key="edit_button")
```

#### Continue Button
```python
st.button("✅ This Looks Right", key="continue_button")
```

#### Edit Mode: Explanation
```python
"See something wrong? Make corrections below and we'll re-analyze."
```

---

## Tab 3: IEP Goal Mapping

### Page Title
```python
st.title("IEP Goal Mapping")
```

### Subtitle
```python
f"Which IEP goals does this work show progress on?"
```

### Goal Matches Section

#### Section Header
```python
"**Matched Goals**"
```

### Goal Match Card (template for each matched goal)

#### Goal Title with Confidence Badge
```python
f"✓ {goal_title} — {confidence_percent}% match"
# Example: "✓ Following Directions — 85% match"
```

#### Confidence Explanation (by range)
```python
confidence_explanations = {
    90: "Crystal clear match. Strong alignment to this goal.",
    85: "Very strong match. Clear connection to goal domain.",
    75: "Good match. Solid evidence of goal progress.",
    60: "Possible match. Some connection, but not certain.",
    40: "Weak match. Unlikely to reflect this goal.",
}
```

#### Trial Data Captured
```python
goal_card_content = f"""
**What we measured:**
- Total trials: 10
- Successes: 7
- Success rate: 70%

**Connection to IEP goal:**
{goal_description}

**What to watch:**
{next_step_recommendation}
"""
```

#### Example Full Goal Match
```python
example_goal_card = """
### Following Directions (G2) — 85% match

**What we measured:**
- Total math problems: 10
- Completed correctly: 7 (70%)
- Student followed multi-step instructions
- Sustained focus across worksheet

**Connection to IEP goal:**
Following written and verbal directions is core to this goal.
The worksheet requires step-by-step task execution.

**Trial Data Recorded:**
- Date: April 3, 2026
- Context: Independent seatwork
- Success rate: 70% (7/10)
- Prompting level: Minimal (student self-started)

**What to watch next:**
Can Maya apply the same direction-following to different tasks?
(Specials, transitions, open-ended activities)
"""
```

### Unmapped Goals Section

#### Section Header
```python
"**Active IEP Goals (no match from this work)**"
```

#### Unmapped Goal Item
```python
"- Peer Greetings (G1) — Not visible in this worksheet"
```

#### Helptext
```python
"Not everything shows progress on every goal. That's normal."
```

### Manual Goal Override (optional)

#### Section Header
```python
"**Don't see the right goal?**"
```

#### Dropdown Label
```python
"Manually assign to a different goal:"
```

#### Dropdown Options (generated from student profile)
```python
# [Goal 1 title, Goal 2 title, Goal 3 title, "Don't map this work"]
```

### Action Buttons

#### Primary: Approve & Continue
```python
st.button("✅ Looks Good — Continue", key="approve_mapping")
```

#### Secondary: Back & Edit
```python
st.button("← Back to Transcription", key="back_to_transcription")
```

---

## Tab 4: Progress Dashboard

### Page Title
```python
st.title("Progress Dashboard")
st.markdown(f"**{student_name}'s IEP Goal Progress**")
```

### Date Range Filter
```python
"Show data from the last:"
date_range_options = ["1 week", "2 weeks", "1 month", "3 months", "All time"]
```

### Goal Progress Card (repeating for each goal)

#### Goal Name & Status Badge
```python
goal_status_badge = {
    "met": "✓ TARGET MET",
    "near": "↗ On Track",
    "plateau": "⚠ Plateau",
    "declining": "↘ Declining",
    "insufficient": "? Insufficient Data",
}

# Example: "Peer Greetings — ✓ TARGET MET"
```

#### Goal Metrics Box
```python
metrics_text = f"""
**Target:** {target_percent}%
**Current:** {current_percent}%
**Baseline:** {baseline_percent}%
**Last {num_trials} trials:** {average_percent}%
"""
```

#### Trend Chart (Plotly line graph)
```python
# Chart title: "Progress Over Time"
# X-axis: Date
# Y-axis: Success %
# Line color: Green (improving), Yellow (stable), Orange (declining)
# Target line: Horizontal dashed line at target_percent
```

#### Trend Description (text below chart)
```python
trend_descriptions = {
    "improving": "📈 Trending upward — Keep doing what you're doing!",
    "stable": "→ Stable performance — On track. No changes needed.",
    "declining": "📉 Trending downward — Time to review your strategy.",
    "plateau": "⏸ Plateau for 3+ weeks — Ready for next intervention?",
    "insufficient": "? Not enough data yet — Check back after 5+ measurements.",
}
```

#### Goal Notes Section (collapsible)

##### Collapsible Header
```python
"📝 Details & Coaching Notes"
```

##### Content (if expanded)
```python
notes_template = f"""
**Last Measurement:** {last_trial_date}
**Measurement Method:** {measurement_method}

**Context from Recent Work:**
{recent_context_note}

**What's Working:**
{intervention_description}

**Next Step:**
{recommendation}

**Important:** {sensory_or_behavioral_note}
"""
```

### Regression Alert (if triggered)

#### Alert Box (critical)
```python
st.error(
    "⚠️ **Regression Detected**\n\n"
    f"**{goal_name}** dropped {percent_drop}% from average.\n\n"
    f"Recent note: {regression_context}\n\n"
    "Review your supports. Is something different?"
)
```

### Goal Mastery Celebration (if met)

#### Celebration Banner
```python
st.success(
    "🎉 **Goal Mastery!**\n\n"
    f"{student_name} has met the target for **{goal_name}**!\n\n"
    "Great work. Consider reducing supports or setting a new goal."
)
```

### Summary Stats (at bottom)

#### Goals Summary Box
```python
summary_text = f"""
**Summary ({date_range})**
- Goals at target: {at_target}/3
- Goals near target: {near_target}/3
- Goals below target: {below_target}/3

**Overall trend:** {overall_trend}

**Most improved goal:** {best_goal}
"""
```

---

## Tab 5: Generated Materials

### Page Title
```python
st.title("Generated Materials")
st.markdown(f"**Materials for {student_name}**")
```

### Filter Buttons

#### Audience Filter
```python
audience_buttons = ["All", "For Teacher", "For Parents", "For Admin"]
```

#### Material Type Filter
```python
type_buttons = [
    "All",
    "Lesson Plans",
    "Tracking Sheets",
    "Social Stories",
    "Visual Schedules",
    "First-Then Boards",
    "Parent Letters",
    "Admin Reports",
]
```

### Generated Material Card (repeating template)

#### Material Title with Icon
```python
card_title = f"📖 Dinosaur Greeting Adventures — Lesson Plan"
```

#### Meta Information
```python
card_meta = f"""
**Created:** April 3, 2026
**For:** Teacher
**Goal:** Peer Greetings
**Theme:** Dinosaurs
"""
```

#### Content Preview (first 200 characters)
```python
card_preview = """
"Maya's Dinosaur Greeting Adventures"

This lesson plan helps Maya practice greeting peers using her favorite dinosaur theme.
Includes 3 hands-on activities and tracking suggestions...
"""
```

#### Action Buttons (on card)
```python
card_buttons = [
    "👁️ View Full",     # Opens full material
    "🖨️ Print",         # Downloads as PDF
    "🔄 Regenerate",    # Deletes and creates new version
]
```

### Approve / Reject Workflow (before printing)

#### Action Prompt (after "View Full")
```python
prompt_text = """
This material looks good to you, yes?

You can:
- ✅ Approve & Save (use it tomorrow)
- ✏️ Edit Text (change a few things)
- 🔄 Regenerate (try again with different content)
- ❌ Delete (skip this material)
"""
```

#### Edit Mode

##### Text Editor Label
```python
"Edit the material before saving:"
```

##### Text Area (with material content)
```python
st.text_area("Material content:", value=material_content, height=300)
```

##### Help Text
```python
"Change anything you'd like. Click Save when done."
```

##### Save Button
```python
st.button("✅ Save Changes", key=f"save_edit_{material_id}")
```

### Empty State (no materials yet)

#### Message
```python
st.info(
    "📝 No materials generated yet.\n\n"
    "Upload student work to see lesson plans, tracking sheets, and more."
)
```

---

## Material Type Specific Copy

### Lesson Plans

#### Header
```python
lesson_plan_header = """
## {Student Interest}-Themed Lesson Plan
**Goal:** {Goal Name}
**For:** {Student Name}, Grade {Grade}
**Theme:** {Student Interest}
"""
```

#### Activity Template
```python
activity_template = """
### Activity {N}: {Activity Name}
**Time:** {5-10 minutes}

**What you do:**
{Step-by-step instruction in simple language}

**Materials:**
- {Item 1}
- {Item 2}

**How to know it worked:**
{Observable outcome}

**Adapted for {Student Name}:**
- Use {interest} theme
- Provide {specific support}
"""
```

#### Reinforcer Section
```python
reinforcer_section = """
**Reinforcers that motivate {Student Name}:**
- {Specific interest item or activity}
- {Sensory preference}
- {Social motivator}
"""
```

### Tracking Sheets

#### Header
```python
tracking_header = """
# {Student Name}'s {Goal} Tracking Sheet
**Goal:** {Goal description}
**Target:** {Target %}
**Tracking method:** {Frequency / Percentage / Duration / Quality}
"""
```

#### Column Headers
```python
tracking_columns = ["Date", "Trial #", "What Happened", "Success?", "Notes"]
```

#### Footer
```python
tracking_footer = """
**Weekly % calculation:**
Total successes ÷ Total trials × 100 = Weekly %

**What to look for:**
{Observable behaviors that = success}

**If performance drops:**
{Quick troubleshooting steps}
"""
```

### Social Stories (Carol Gray Format)

#### Header
```python
social_story_header = """
# {Story Title}
**For:** {Student Name}
**About:** {Situation}
"""
```

#### Format Note (for teacher)
```python
format_note = """
*This social story uses the Carol Gray format:*
- First-person perspective ("I")
- 2 descriptive sentences : 1 coaching sentence ratio
- Concrete language, short sentences
- Visual supports recommended
"""
```

#### Example Story Sentences
```python
example_story = """
My name is Maya. I like dinosaurs.

Transitions mean we move from one activity to another.
Everyone in our class has transitions.
I can be brave during transitions like Blue the raptor.

Sometimes transitions feel bumpy or loud.
My body might feel worried.
I can use my noise-canceling headphones to help.
"""
```

### Visual Schedules

#### Header
```python
visual_schedule_header = """
# {Student Name}'s {Routine} Schedule
**Skills:** Following transitions, predicting what comes next
"""
```

#### Step Template
```python
step_template = """
[IMAGE] {Step Number}. {Activity Name}

*Sensory note: {Sensory element if relevant}*
"""
```

#### Reinforcement Note
```python
reinforcement_note = "Small {interest}-themed sticker or token for each completed step."
```

### First-Then Boards

#### Header
```python
first_then_header = """
# First-Then Board for {Student Name}
**Used for:** Transitions, difficult tasks, choices
"""
```

#### Card Template
```python
first_then_card = """
[TOP IMAGE] FIRST: {Preferred Activity}

[ARROW]

[BOTTOM IMAGE] THEN: {Required Activity}
"""
```

### Parent Communications

#### Letter Header
```python
letter_header = """
Hi {Parent Name},

{Student Name} had a great day today!
"""
```

#### Progress Section Template
```python
progress_section = """
**{Student Name} worked on {Goal Name} today:**

{Specific behavior observed from today's work}.
This shows {how it connects to goal}.
{Celebration or growth note}.
"""
```

#### Home Practice Template
```python
home_practice = """
**Try this at home:**

{Simple 1-2 activity description based on student interest}

Example: "{Concrete example}."

This helps {student name} practice {goal} in a fun way.
"""
```

#### Closing Template
```python
closing = """
Thanks for all you do to support {student name}.
We're celebrating {his/her/their} progress every day.

Best,
{Teacher Name}
"""
```

### Admin Reports

#### Report Header
```python
report_header = """
# {Student Name} — Progress Summary
**Report Period:** {Start Date} to {End Date}
**Teacher:** {Teacher Name}
**Grade:** {Grade}
"""
```

#### Goal Summary Template
```python
goal_summary = """
### {Goal Name} ({Goal ID})

| Metric | Value |
|--------|-------|
| Baseline | {Baseline %} |
| Current | {Current %} |
| Target | {Target %} |
| Status | {Status Badge} |
| Trend | {Trend} |

**Intervention:**
{Specific strategy and materials used}

**What's working:**
{Evidence from data}

**Next step:**
{Recommendation for maintaining or advancing}
"""
```

#### Summary Statement
```python
summary_statement = """
**Summary:**

{Student name} has made {progress description} progress toward
{number} IEP goals through {intervention strategy}.
{He/She/They} demonstrates {skill area} across multiple settings.

**Recommendation:**
{Next phase of instruction or goal setting}
"""
```

---

## Buttons & CTAs (Global)

### Primary Action Buttons
```python
primary_button_copy = {
    "upload": "🚀 Upload & Analyze",
    "continue": "✅ This Looks Right",
    "save": "💾 Save Changes",
    "approve": "✅ Approve & Save",
    "print": "🖨️ Print to PDF",
    "regenerate": "🔄 Regenerate",
}
```

### Secondary Action Buttons
```python
secondary_button_copy = {
    "back": "← Back",
    "edit": "✏️ Edit",
    "demo": "👁️ Try Demo",
    "delete": "🗑️ Delete",
    "cancel": "✕ Cancel",
    "help": "? Help",
}
```

### Confirmation Dialogs

#### Delete Warning
```python
delete_dialog = """
Are you sure? This can't be undone.

Click "Yes, Delete" to remove {material_name}.
"""
```

#### Leave without Saving
```python
unsaved_dialog = """
You have unsaved changes to {material_name}.

- ✅ Save & Exit
- ❌ Exit without saving
"""
```

---

## Error & Validation Messages

### Form Validation

#### Missing Required Field
```python
validation_error = "Please choose a work type above."
```

#### File Format Error
```python
file_error = "We need a JPG, PNG, or PDF. Check your file type and try again."
```

#### File Size Error
```python
size_error = "Photo is too large (max 10 MB). Try a smaller file."
```

#### Image Quality Warning
```python
quality_warning = (
    "📸 This photo is blurry or dark. "
    "Try a clearer, well-lit photo for better results."
)
```

### API Errors

#### Generic Failure
```python
api_error = (
    "❌ Oops! Something went wrong.\n\n"
    "Try again in a moment. If this keeps happening, contact support."
)
```

#### Rate Limit / Timeout
```python
timeout_error = (
    "⏳ Analysis is taking longer than expected.\n\n"
    "Please wait a moment and try again, or come back in a few minutes."
)
```

#### No Internet Connection
```python
offline_error = (
    "❌ No internet connection.\n\n"
    "Check your connection and try again."
)
```

---

## Tooltips & Help Text

### Photo Upload Help
```python
upload_help = (
    "📸 **Tips for good photos:**\n"
    "- Use natural light (window or outside)\n"
    "- Avoid shadows across the page\n"
    "- Take photo straight-on (not at an angle)\n"
    "- Make sure handwriting is clear\n\n"
    "Blurry or dark photos may not work well."
)
```

### Confidence Score Help
```python
confidence_help = (
    "**How confident are we in this match?**\n"
    "- 90%+: Crystal clear. Strong evidence.\n"
    "- 75-89%: Very strong. Clear connection.\n"
    "- 60-74%: Good match. Some connection.\n"
    "- Below 60%: Weak. Not sure if it fits.\n\n"
    "If we're wrong, you can change it manually."
)
```

### Trial Data Help
```python
trial_help = (
    "**What's a 'trial'?**\n"
    "One attempt at the skill. On this worksheet, "
    "each math problem = 1 trial."
)
```

### Prompting Level Help
```python
prompting_help = (
    "**Prompting levels (how much help):**\n"
    "- Independent: Student did it alone\n"
    "- Spatial: Teacher pointed or gestured\n"
    "- Verbal: Teacher gave instructions\n"
    "- Model: Teacher showed how\n"
    "- Physical: Teacher guided hand-over-hand"
)
```

### Trend Explanation
```python
trend_help = (
    "**What do these trend labels mean?**\n"
    "- **Improving:** Getting better over time\n"
    "- **Stable:** Staying about the same\n"
    "- **Declining:** Getting worse\n"
    "- **Plateau:** Stuck at same level for 3+ weeks\n"
    "- **Insufficient Data:** Need 5+ measurements to detect a trend"
)
```

---

## Alerts & Notifications

### Success Messages

#### Upload Success
```python
st.success("✅ Photo uploaded and analyzed successfully!")
```

#### Material Generated
```python
st.success(
    f"✅ {material_name} created!\n\n"
    "Review it below. Approve to save or regenerate for a different version."
)
```

#### Goal Met Celebration
```python
st.balloons()
st.success(
    f"🎉 **Amazing progress!**\n\n"
    f"{student_name} has met the target for **{goal_name}**.\n\n"
    "Well done. Consider setting a new goal or fading supports."
)
```

### Warning Messages

#### Plateau Alert
```python
st.warning(
    f"⏸ **Plateau detected for {goal_name}**\n\n"
    "This goal has been stuck at the same level for 3+ weeks. "
    "Time to review your intervention strategy. "
    "Would a different approach help?"
)
```

#### Regression Alert
```python
st.error(
    f"📉 **Performance dropped on {goal_name}**\n\n"
    f"Down {percent_drop}% from the average.\n\n"
    "What's different? Check for:\n"
    "- Changes in routine or setting\n"
    "- Sensory issues or fatigue\n"
    "- Need for adjusted supports"
)
```

#### Low Confidence Warning
```python
st.warning(
    "⚠️ **We're not fully confident in this match.**\n\n"
    "The work might connect to a different goal. "
    "Review the mapping and adjust if needed."
)
```

### Info Messages

#### Demo Mode Disclaimer
```python
st.info(
    "🎯 **Demo Mode**\n\n"
    "You're seeing sample data. Upload your own photos to analyze "
    "your student's real work."
)
```

#### Feature Explanation
```python
st.info(
    "💡 **What's a social story?**\n\n"
    "A short, personalized story that helps students understand "
    "situations and expectations. Written in first person, "
    "often with pictures."
)
```

---

## Footer & Attribution

### App Footer
```python
footer_text = """
---

**ClassLens ASD** — Built with Gemma 4 for the Gemma 4 Good Hackathon

[Docs](https://github.com/jallanaleven/classlens-asd) |
[GitHub](https://github.com/jallanaleven/classlens-asd) |
[Report a Bug](mailto:jeff@fairfaxsoftware.com)

*Data is stored locally on your computer. Nothing is shared or sold.*
"""
```

### Version Info
```python
version_info = "ClassLens ASD v1.0 (Demo) — April 2026"
```

---

## Accessibility & Alternative Text

### Image Alt Text Examples

#### Student Profile Photo
```python
alt_text = f"Photo of {student_name} working on a math worksheet"
```

#### Goal Progress Chart
```python
alt_text = f"Line graph showing {goal_name} progress from {start_date} to {end_date}. Trend: {trend}."
```

#### Uploaded Work Photo
```python
alt_text = f"Photo of {work_type} completed by {student_name} on {date}"
```

### Icon Explanations (for screen readers)
```python
icon_explanations = {
    "✓": "Check mark - Complete, correct, or on track",
    "✗": "X mark - Incorrect or not completed",
    "⚠": "Warning sign - Needs attention",
    "📈": "Upward trend - Improving",
    "📉": "Downward trend - Declining",
    "→": "Horizontal line - Stable",
    "⏸": "Pause symbol - Plateau",
    "?": "Question mark - Insufficient data",
}
```

---

## Microcopy: Empty States & Edge Cases

### No Students Loaded
```python
empty_state = (
    "No students found.\n\n"
    "Contact your administrator to set up your student roster."
)
```

### No Goals for Student
```python
no_goals_state = (
    "No active IEP goals for this student yet.\n\n"
    "Goals will appear here as you upload work."
)
```

### No Trial History
```python
no_history_state = (
    "No trial data yet. Upload student work to start tracking progress."
)
```

### No Materials Generated
```python
no_materials_state = (
    "No materials generated yet.\n\n"
    "Upload student work and approve goal mappings to generate "
    "lesson plans, tracking sheets, and more."
)
```

### First-Time User Guidance
```python
first_time_guidance = """
**Welcome to ClassLens ASD!**

Here's how to get started:

1. **Select a student** from the sidebar
2. **Upload a photo** of their work (math, checklist, writing, etc.)
3. **Review what we see** — correct any transcription errors
4. **Check goal matches** — confirm which IEP goals this shows
5. **View progress** on the dashboard
6. **Generate materials** (lesson plans, parent letters, tracking sheets)

Ready? Choose a student above and upload a photo.
"""
```

---

## Student-Specific Customization

### Maya's Customizations
```python
maya_custom = {
    "interest": "Dinosaurs",
    "example_reinforcer": "dinosaur stickers",
    "sensory_note": "Loves deep pressure and fidgets",
    "communication": "Verbal, 3-4 word phrases",
}
```

### Jaylen's Customizations
```python
jaylen_custom = {
    "interest": "Trains (Thomas the Tank Engine)",
    "example_reinforcer": "5 minutes of Thomas videos",
    "sensory_note": "Seeks spinning/movement; sensitive to loud sounds",
    "communication": "Non-verbal AAC user; responds to visual supports",
}
```

### Sofia's Customizations
```python
sofia_custom = {
    "interest": "US Presidents and Maps",
    "example_reinforcer": "Researching new presidents or maps",
    "sensory_note": "Anxious about unexpected changes; needs advance notice",
    "communication": "Verbal, full sentences; strong reader",
}
```

---

## Copy Formatting Rules (for Developers)

### All Primary Buttons
```python
# Format: Emoji + Action Verb + Object
# Examples: "🚀 Upload & Analyze", "✅ Approve & Save", "🖨️ Print to PDF"
# Rule: Keep under 25 characters
```

### All Headings
```python
# Use consistent emoji + bold text
# Level 1: st.title() — Largest, page title
# Level 2: st.markdown("**Subheading**") — Section headers
# Level 3: st.markdown("### Subheading") — Detail section headers
```

### All Field Labels
```python
# Format: "Clear question or direction"
# End with colon only if followed by input
# Examples:
#   "What type of work?" (question, no colon)
#   "Student name:" (label with colon)
```

### All Error Messages
```python
# Format: ❌ [Problem] + Reason + One Clear Action
# Example: "❌ Photo too large (max 10 MB). Try a smaller file."
```

### All Success Messages
```python
# Format: ✅ [What Happened] + Optional Celebration
# Example: "✅ Goal met! Amazing progress on Greetings."
```

---

## Copy Checklist (QA)

Before deploying any new copy:

- [ ] No jargon (no "inference," "confidence score," "multimodal," "token")
- [ ] Short sentences (max 15 words)
- [ ] Active voice where possible
- [ ] All button labels start with emoji
- [ ] All errors include one clear next action
- [ ] All success messages celebrate genuinely (not patronizing)
- [ ] Student interests (dinosaurs, trains, presidents) personalized
- [ ] Grade-level language matches student profile
- [ ] Sensory/behavioral notes included where relevant
- [ ] Tested for readability (Flesch-Kincaid Grade 5 or below)

