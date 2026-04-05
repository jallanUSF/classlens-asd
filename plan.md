# UI/UX Redesign Plan

## Goal
Reorganize 5 feature-tabs into 3 workflow-views. Modernize visual design.
Full design spec: `docs/plans/2026-04-04-ui-redesign.md`

## Phase 1: Layout + Navigation
- [ ] Replace tabs with 3-view nav in app.py
- [ ] Update ui/styles.py with new design system CSS
- [ ] Wire st.session_state["active_view"] routing

## Phase 2: My Students View
- [ ] Create ui/students_view.py — card grid
- [ ] Click handler: select student + switch to Capture

## Phase 3: Capture & Create View
- [ ] Create ui/capture_view.py — two-column layout
- [ ] Left: upload + analyze + results
- [ ] Right: material tile grid + inline generation

## Phase 4: Progress & Reports View
- [ ] Create ui/progress_view.py — dashboard + admin reports merged
- [ ] Fix underscore labels in domain names

## Phase 5: Polish + QA
- [ ] Playwright visual QA — every view, every state
- [ ] Test all 3 students end-to-end
- [ ] Verify Streamlit Cloud deployment
