# UX Copy Reference — Quick Navigation Index

Use this index to quickly find the copy you need for ClassLens ASD.

## Find Copy By Screen

### Sidebar & Navigation
- **Student Selector**: "Select a Student" button group
- **Navigation Tabs**: Upload | Dashboard | Goals | Materials

→ See section: "Sidebar Navigation"

### Upload Work Screen (Tab 1)
- Work type selection (7 types)
- Photo upload widget
- Date & context inputs
- Action buttons
- All states: empty, loading, error, success

→ See sections: "Tab 1: Upload Work" + "Upload States"

### Vision Reader Results (Tab 2)
- Transcription examples for each work type
- Edit/approve workflow
- Confidence explanations

→ See section: "Tab 2: Vision Reader Results"

### IEP Goal Mapping (Tab 3)
- Goal match cards
- Confidence badges
- Manual override
- Approval workflow

→ See section: "Tab 3: IEP Goal Mapping"

### Progress Dashboard (Tab 4)
- Date range filter
- Goal status badges (met, near, plateau, declining, insufficient)
- Trend charts & descriptions
- Regression & mastery alerts
- Summary stats

→ See section: "Tab 4: Progress Dashboard"

### Generated Materials (Tab 5)
- Material cards (title, meta, preview)
- Filter buttons (audience, type)
- Approve/edit/regenerate workflow

→ See section: "Tab 5: Generated Materials"

## Find Copy By Feature

### Buttons & CTAs
All buttons with emoji and action verb (e.g., "🚀 Upload & Analyze")

→ See section: "Buttons & CTAs (Global)"

### Error Messages
All validation, API, and file errors

→ See section: "Error & Validation Messages"

### Success Messages
Upload success, material generation, goal celebrations

→ See section: "Alerts & Notifications" > "Success Messages"

### Warnings & Alerts
Plateau detection, regression alerts, confidence issues

→ See section: "Alerts & Notifications" > "Warning Messages"

### Help Text & Tooltips
How to upload good photos, what confidence means, trend explanations

→ See section: "Tooltips & Help Text"

### Empty States
No students, no goals, no history, no materials yet

→ See section: "Microcopy: Empty States & Edge Cases"

### Material Templates
Lesson plans, tracking sheets, social stories, schedules, parent letters, admin reports

→ See section: "Material Type Specific Copy"

## Find Copy By Student

### Maya (Grade 3, Dinosaurs)
- All mentions of "dinosaurs" and "dinosaur-themed"
- Example: "Maya's Dinosaur Greeting Adventures"

→ See section: "Student-Specific Customization" > "Maya's Customizations"
→ Also search: "dinosaur" in full document

### Jaylen (Grade 1, Non-verbal AAC, Trains)
- All mentions of "trains" and "Thomas"
- AAC-specific language and prompting

→ See section: "Student-Specific Customization" > "Jaylen's Customizations"
→ Also search: "train" or "AAC" in full document

### Sofia (Grade 5, Presidents/Maps)
- Schedule change anxiety support
- Advanced reader language
- Map/president metaphors

→ See section: "Student-Specific Customization" > "Sofia's Customizations"
→ Also search: "president" or "map" in full document

## Find Copy By Message Type

### Form Labels & Input Instructions
- Work type selector
- Date picker
- Text area labels

→ See section: "Tab 1: Upload Work" (subsections for each input)

### Status Badges
- ✓ TARGET MET
- ↗ On Track
- ⚠ Plateau
- ↘ Declining
- ? Insufficient Data

→ See section: "Tab 4: Progress Dashboard" > "Goal Progress Card"

### Explanations & Educational Copy
- Carol Gray social story format
- Prompting levels definition
- Trial data definition
- Trend meanings

→ See section: "Tooltips & Help Text"

### Celebrations & Affirmations
- Goal mastery balloons
- Progress acknowledgment
- Genuine encouragement

→ See section: "Alerts & Notifications" > "Success Messages"

### Parent-Facing Copy
- Parent letter templates
- Home practice activities
- Celebration language

→ See section: "Material Type Specific Copy" > "Parent Communications"

### Administrator-Facing Copy
- Admin report structure
- Intervention descriptions
- Recommendation language

→ See section: "Material Type Specific Copy" > "Admin Reports"

## Find Copy By Word/Phrase

### Common Phrases
- "student work" — replace jargon like "artifact"
- "success percentage" — specific measurement language
- "trending upward" — trend descriptions
- "Here's what the student..." — Vision Reader intro
- "Where's the evidence?" — Critical thinking prompts

### All Emojis Used
- 📸 Upload / Photos
- 📊 Dashboard / Data
- 🎯 Goals
- 📝 Materials / Writing
- ✓ Success / Complete
- ✗ Incorrect / Incomplete
- ⚠ Warning / Alert
- 📈 Improving / Upward
- 📉 Declining / Downward
- 🎉 Celebration
- ❌ Error
- ⏳ Loading / Wait
- 💾 Save
- 🖨️ Print
- 🔄 Regenerate
- 🗑️ Delete
- ✏️ Edit
- 👁️ View
- ? Help / Question
- ⏸ Pause / Plateau

## How to Use This Reference

1. **Find your screen** (Upload, Dashboard, Materials, etc.)
2. **Locate the section** in UX-COPY-REFERENCE.md
3. **Copy the text** (all strings are ready-to-paste Python)
4. **Paste into your Streamlit code**
5. **Substitute placeholders** ({Student Name}, {Goal}, etc.)
6. **Test with a real teacher** before shipping

## Copy Quality Checklist

Before deploying any copy to production:
- [ ] No jargon (no "inference," "confidence score," "multimodal")
- [ ] Short sentences (avg 12 words, max 15)
- [ ] Active voice where possible
- [ ] Button labels start with emoji
- [ ] Errors include ONE clear next action
- [ ] Success messages celebrate genuinely
- [ ] Student interests personalized (dinosaurs, trains, presidents)
- [ ] Grade-level language appropriate
- [ ] Sensory/behavioral notes where relevant
- [ ] Readability check (Flesch-Kincaid Grade 5 or below)

## Versioning & Updates

**Current Version:** 1.0 (April 2026)
**Last Updated:** April 4, 2026
**Next Review:** After first teacher pilot (May 2026)

If copy needs updating:
1. Edit UX-COPY-REFERENCE.md
2. Bump version number
3. Update this index if sections change
4. Notify dev team of affected screens

## Contact & Questions

Questions about the copy?
- Check the "Design Principles" section at the top
- Review the "Copy Checklist" section
- Ask: "Would a busy K-12 teacher understand this?"

---

**Ready to build?** Open UX-COPY-REFERENCE.md and find your screen.
