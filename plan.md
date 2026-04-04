# Sprint 3 Plan — Polish, Test, Deploy

## Goal
Fix known issues, add tests, generate precomputed demo data, deploy to Streamlit Cloud.
End state: public URL that judges can visit and get a flawless demo experience.

## What's Done (Sprints 1-2)
- All 4 agents built and wired into pipeline
- Full Streamlit app with 5 tabs
- Works in demo mode (mock client) but MockGemmaClient interface incomplete
- No precomputed results cached yet
- No tests written yet

## Sprint 3 Build Order

### 1. Fix MockGemmaClient (Critical — unblocks everything else)
Update `tests/mock_api_responses.py` so MockGemmaClient has:
- `generate(prompt, system)` → returns text
- `generate_multimodal(image_path, prompt, system)` → returns text
- `generate_with_tools(prompt, tools, system, image_path)` → returns {"function": ..., "args": {...}}
- `generate_with_thinking(prompt, system)` → returns {"thinking": ..., "output": ...}
Returns realistic mock data for each student's sample work images.

### 2. Generate precomputed demo results
Run full pipeline on all sample images with either real API or fixed mock.
Populate `data/precomputed/` so demo loads instantly.

### 3. Reconcile Pydantic models (optional, low priority)
Either update student JSON to match Pydantic schema, or update Pydantic to match JSON.
Not blocking — agents use raw dicts.

### 4. Write core tests
- test_state_store.py — CRUD operations
- test_pipeline.py — end-to-end with mock client
- test_agents.py — each agent with mock responses

### 5. Deploy to Streamlit Cloud (Phase 5)
- Connect GitHub repo to Streamlit Cloud
- Set GOOGLE_AI_STUDIO_KEY as secret
- Verify public URL works
- Test on mobile

### 6. Kaggle notebook (Phase 5)
- `notebooks/classlens_demo.ipynb` — step-by-step pipeline walkthrough
