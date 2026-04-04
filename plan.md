# Sprint 2 Plan — Material Forge + Demo App

## Goal
Complete Phase 3 (Material Forge agent) and Phase 4 (Streamlit demo app).
End state: working Streamlit app with upload, dashboard, materials viewer, and admin reports.

## What's Done (Sprint 1)
- core/gemma_client.py — Gemma 4 API wrapper
- schemas/tools.py — All 8 function calling schemas
- agents/base.py, vision_reader.py, iep_mapper.py, progress_analyst.py
- core/pipeline.py — End-to-end orchestration with precomputed caching
- prompts/templates.py — All prompt templates ready

## Sprint 2 Build Order

### Phase 3: Material Forge (Agent 4)
1. agents/material_forge.py — All 7 output types using function calling
   - generate_lesson_plan() — Sarah's #1 request
   - generate_tracking_sheet()
   - generate_social_story() — Carol Gray framework
   - generate_visual_schedule()
   - generate_first_then()
   - generate_parent_comm()
   - generate_admin_report()

### Phase 4: Demo App
2. app.py — Streamlit entry point with navigation
3. ui/styles.py — ASD-friendly CSS
4. ui/upload.py — Student selector + image upload + process
5. ui/dashboard.py — Per-student goal cards with Plotly trend charts
6. ui/outputs.py — Tabbed view of generated materials with approve/edit
7. ui/lesson_planner.py — Goal → lesson plan + tracking sheet
8. ui/reports.py — Admin progress reports
