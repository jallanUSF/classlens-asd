# Sprint 4 Plan — Polish & Submission Prep

## Goal
Finalize competition writeup, polish the demo experience, fix any UI bugs.
End state: everything a judge touches works flawlessly.

## What's Done (Sprints 1-3)
- All 4 agents built and wired into pipeline
- Full Streamlit app with 5 tabs
- MockGemmaClient complete, 35 tests passing
- Precomputed demo results cached
- Kaggle notebook created
- GitHub repo pushed

## Sprint 4 Build Order

### 1. Fix competition writeup placeholders
Update COMPETITION-WRITEUP.md: real GitHub link, remove stale placeholders,
ensure code snippets match actual implementation.

### 2. Smoke-test the Streamlit app end-to-end
Run the app, click through every tab with each student, verify:
- Sidebar student selection works
- Upload tab: sample images load, pipeline runs, results display
- Dashboard: Plotly charts render for all 3 students
- Materials: all 7 output types generate
- Lesson Planner: generates and displays
- Admin Reports: charts + report generate

### 3. Fix any UI bugs found during smoke test

### 4. Polish demo flow for judges
- Ensure first-time experience is clear (no student selected → helpful message)
- Precomputed results load instantly
- Error states handled gracefully

### 5. Finalize ADR and security docs
