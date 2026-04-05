# UI/UX Redesign Plan

## Goal
Reorganize 5 feature-tabs into 3 workflow-views. Modernize visual design.
Full design spec: `docs/plans/2026-04-04-ui-redesign.md`

## Phase 1: Layout + Navigation ✅
- [x] Replace tabs with 3-view nav in app.py
- [x] Update ui/styles.py with new design system CSS
- [x] Wire st.session_state["active_view"] routing

## Phase 2: My Students View ✅
- [x] Create ui/students_view.py — card grid
- [x] Click handler: select student + switch to Capture

## Phase 3: Capture & Create View ✅
- [x] Create ui/capture_view.py — two-column layout
- [x] Left: upload + analyze + results
- [x] Right: material tile grid + inline generation

## Phase 4: Progress & Reports View ✅
- [x] Create ui/progress_view.py — dashboard + admin reports merged
- [x] Fix underscore labels in domain names

## Phase 5: Polish + QA ✅
- [x] Playwright visual QA — every view, every state
- [x] Test all 3 students end-to-end
- [x] 35/35 tests passing
