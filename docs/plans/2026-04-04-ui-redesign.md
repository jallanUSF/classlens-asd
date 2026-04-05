# UI/UX Redesign Plan — ClassLens ASD

**Date:** 2026-04-04
**Goal:** Reorganize from 5 feature-tabs to 3 workflow-views, modernize visual design, make it feel like Sarah's daily tool.

---

## Architecture: 5 Tabs → 3 Views

### Current (5 tabs, feature-organized)
1. Upload Work
2. Progress Dashboard
3. Generated Materials
4. Lesson Planner
5. Admin Reports

**Problems:** Tab labels truncate. Lesson Planner and Generated Materials overlap. Teacher has to bounce between tabs. Empty states everywhere until student selected.

### New (3 views, workflow-organized)

**View 1: My Students** (home, shown when no student selected)
- Grid of student cards: name, grade, ASD level badge, interest emoji, goal count, sparkline trend
- Click card → selects student, switches to Capture & Create
- File: `ui/students_view.py`

**View 2: Capture & Create** (merge of Upload + Generated Materials + Lesson Planner)
- Two-column layout
- Left: image upload/select → analyze → results inline
- Right: material generation tiles (6 icon buttons), outputs stack below
- File: `ui/capture_view.py`

**View 3: Progress & Reports** (merge of Dashboard + Admin Reports)
- Summary metrics row
- Goal cards with Plotly charts (reuse existing `_render_goal_card`, `_make_trend_chart`)
- Admin report generator at bottom
- File: `ui/progress_view.py`

**Navigation:** Custom styled buttons in `st.columns`, not Streamlit tabs. Tracked via `st.session_state["active_view"]`.

---

## Visual Design System

### Colors
| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#5B8FB9` | Headers, nav, chart lines |
| Accent | `#4ECDC4` | Success, CTAs, active states |
| Warm | `#F7B267` | Highlights, interest badges |
| Background | `#FAFAFA` | Main area |
| Sidebar BG | `#F0F4F8` | Sidebar |
| Card BG | `#FFFFFF` | Card surfaces |
| Text Primary | `#2C3E50` | Body text |
| Text Secondary | `#7F8C8D` | Captions, labels |
| Level 1 | `#4ECDC4` | ASD Level 1 badge |
| Level 2 | `#5B8FB9` | ASD Level 2 badge |
| Level 3 | `#9B59B6` | ASD Level 3 badge |

### Student Cards
```
┌─────────────────────────┐
│  🦕  Maya               │
│  Grade 3 · Level 2      │  <- color-coded badge
│  ──────────── 80% ↑     │  <- mini sparkline + trend
│  3 goals · 19 sessions  │
└─────────────────────────┘
```
Interest emoji mapping: Maya → 🦕, Jaylen → 🚂, Sofia → 🌍

### Cards & Containers
- White background, `border-radius: 12px`, subtle `box-shadow: 0 2px 8px rgba(0,0,0,0.06)`
- Active/selected cards: left border 4px accent color
- Metric cards: gradient left border (primary → accent)

### Buttons
- Primary: filled `#5B8FB9`, white text, `border-radius: 8px`
- Secondary: outline style
- Material tiles: 60x60 icon buttons in a 3x2 grid, subtle hover lift

### Typography
- H1: 1.8rem, `#2C3E50`, bottom border primary
- H2: 1.3rem, `#2C3E50`
- H3: 1.1rem, `#5B8FB9`
- Body: system sans-serif, `#2C3E50`
- Caption: 0.85rem, `#7F8C8D`

---

## Capture & Create View Detail

### Left Column: Capture
1. Student context bar: emoji + name + grade + date
2. Work type selector (dropdown)
3. Image source: sample or upload (radio)
4. Image preview (larger than current — 500px width)
5. "Analyze" button (primary, full width)
6. After analysis: summary cards (items, goals, alerts) + expandable details

### Right Column: Create Materials
Before analysis: grayed out placeholder with lock icon
After analysis (or always available): 6 material tiles in 3x2 grid:

| Tile | Label | Method |
|------|-------|--------|
| 📝 | Lesson Plan | `generate_lesson_plan` |
| 📊 | Tracking Sheet | `generate_tracking_sheet` |
| 📖 | Social Story | `generate_social_story` |
| 📅 | Visual Schedule | `generate_visual_schedule` |
| 🏠 | Parent Letter | `generate_parent_comm` |
| 📋 | Admin Report | `generate_admin_report` |

Click tile → generates inline → output card appears below with Approve/Regenerate/Download PDF

### Social Story & Visual Schedule
These need extra inputs (scenario, routine). When clicked, a small input field appears above the output area before generating.

---

## Progress & Reports View Detail

### Top: Summary Metrics
Row of 3-4 metric cards: Active Goals, Total Data Points, Overall Average, Trend

### Middle: Goal Cards
Reuse existing `_render_goal_card` and `_make_trend_chart` from `ui/dashboard.py`.
Fix: `Following_Directions` → `Following Directions` (replace underscores in domain display).

### Bottom: Admin Report
- Multi-goal Plotly chart (reuse `_render_multi_goal_chart`)
- "Generate Full Report" button
- Report output with approve/regenerate

---

## Sidebar Redesign

### Always visible:
- App logo/title area (compact)
- Student list as compact cards (not full buttons)
- Active student highlighted with accent left border
- Footer: version + hackathon info

### When student selected:
- Below student list: profile summary
  - Communication level
  - Interests (with emoji)
  - Sensory notes (brief)
  - Goal count

---

## Implementation Order

### Phase 1: New layout + navigation (app.py + styles)
1. Replace tabs with 3-view navigation in `app.py`
2. Update `ui/styles.py` with new CSS design system
3. Wire `st.session_state["active_view"]` routing

### Phase 2: My Students view
4. Create `ui/students_view.py` — student card grid
5. Click handler: set student + switch to Capture view

### Phase 3: Capture & Create view
6. Create `ui/capture_view.py` — two-column layout
7. Left: migrate upload logic from `ui/upload.py`
8. Right: material tile grid + inline generation
9. Migrate generation logic from `ui/outputs.py` and `ui/lesson_planner.py`

### Phase 4: Progress & Reports view
10. Create `ui/progress_view.py` — merge dashboard + admin reports
11. Migrate chart logic from `ui/dashboard.py`
12. Migrate report logic from `ui/reports.py`
13. Fix underscore labels in domain names

### Phase 5: Polish + QA
14. Visual QA with Playwright — screenshot every view, every state
15. Test all 3 students
16. Test analyze → generate → approve flow end-to-end
17. Verify Streamlit Cloud deployment works

---

## Files Changed

### New files:
- `ui/students_view.py`
- `ui/capture_view.py`
- `ui/progress_view.py`

### Modified files:
- `app.py` — new navigation, remove tabs
- `ui/styles.py` — new design system CSS

### Deprecated (keep but unused):
- `ui/upload.py` — logic migrated to capture_view
- `ui/outputs.py` — logic migrated to capture_view
- `ui/lesson_planner.py` — logic migrated to capture_view
- `ui/dashboard.py` — logic migrated to progress_view
- `ui/reports.py` — logic migrated to progress_view

---

## Constraints
- Must work on Streamlit Community Cloud (no custom JS components)
- ASD-friendly: no animations, no surprises, predictable layouts, calm colors
- All `st.markdown(unsafe_allow_html=True)` for custom HTML/CSS
- Precomputed/mock results must still work (demo mode)
- 35 existing tests must still pass
