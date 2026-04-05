# Sprint 5 Plan — Ship It (continued)

## Goal
Finish submission: update writeup with live URLs, re-upload notebook to Kaggle, record video, submit.
Deadline: May 18, 2026.

## What's Done
- Streamlit Cloud deployed and public
- Kaggle notebook uploaded (needs re-upload with executed outputs)
- PDF report generator working (21 PDFs across 3 students)
- All SDK compatibility issues fixed (model name, tools, thinking)
- 35 tests passing

## Remaining Tasks

### 1. Update COMPETITION-WRITEUP.md
- Add live demo URL: `classlens-asd-bbdjgeutrjozwopvsyw6qo.streamlit.app`
- Update model name: `gemma-4-31b-it` (not `gemma-4-27b-it`)
- Add PDF report generation as a feature (5th agent capability)
- Add link to sample PDF outputs in `outputs/`

### 2. Re-upload Kaggle notebook
- Upload `notebooks/classlens_demo_executed.ipynb` (has all outputs baked in)
- Just save — no need to run. Judges see the outputs immediately.
- Rename from `notebook0df7597f7c` to `ClassLens ASD Demo`

### 3. Record video (Jeff + Sarah)
- Follow `docs/VIDEO-SCRIPT.md`
- 3 minutes max, 1080p
- Show: live demo URL, pipeline results, PDF reports, dashboard

### 4. Submit to Kaggle
- Competition writeup from `docs/COMPETITION-WRITEUP.md`
- Links: GitHub, live demo, Kaggle notebook, video

### 5. Optional: Ollama edge demo
- Install ollama, pull gemma-4-e4b (or gemma-3n-e4b-it which is available)
- Add OLLAMA backend to `core/gemma_client.py`
- Qualifies for Special Tech track
