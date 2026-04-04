# Sprint 5 Plan — Ship It

## Goal
Get everything submitted: live URL, Kaggle notebook, video, competition entry.
Deadline: May 18, 2026.

## What's Done (Sprints 1-4)
- All 4 agents built and wired into pipeline
- Full Streamlit app with 5 tabs, ASD-friendly CSS
- MockGemmaClient complete with accurate routing
- 35 tests passing
- 4 precomputed demo results cached
- Kaggle notebook (32 cells, 10 sections)
- Competition writeup finalized
- ADR, security review, video script, UX copy all done
- GitHub repo public: jallanUSF/classlens-asd

## Sprint 5 Build Order

### 1. Deploy to public URL
Options (pick one):
- **Streamlit Cloud**: share.streamlit.io → New app → jallanUSF/classlens-asd, master, app.py
- **HF Spaces**: Create new Space (Streamlit SDK), push code, set API key as secret
- **Railway**: Connect GitHub, set GOOGLE_AI_STUDIO_KEY env var

App works without API key — precomputed results + MockGemmaClient fallback.

### 2. Upload Kaggle notebook
- Go to kaggle.com/code → New Notebook → Upload notebooks/classlens_demo.ipynb
- Add-ons → Secrets → GOOGLE_AI_STUDIO_KEY
- Settings → Enable Internet
- Run all cells, verify outputs
- Make notebook public

### 3. Record video (Jeff + Sarah)
- Follow docs/VIDEO-SCRIPT.md shot list
- 3 minutes max, 1080p
- Demo flow: problem → solution → live demo → impact
- Pre-bake all results (they're cached — demo never waits)

### 4. Submit to Kaggle
- Competition writeup: paste from docs/COMPETITION-WRITEUP.md
- Links: GitHub repo, live demo URL, Kaggle notebook, video
- Tracks: Education + Main (possibly Special Tech if Ollama demo added)

### 5. Optional: Ollama edge demo
- Install ollama, pull gemma-4-e4b
- Add OLLAMA backend to core/gemma_client.py
- Demo: run pipeline fully local, no internet
- Qualifies for Special Tech track
