# Sprint 1 Plan — Foundation + Agent Pipeline

## Goal
Complete Phase 1 (foundation) and Phase 2 (agent pipeline) from IMPLEMENTATION-PLAN.md.
End state: full pipeline runs image → transcription → IEP mapping → progress analysis.

## What's Done (Phase 1 partial)
- Project structure, all __init__.py files
- schemas/student_profile.py — Pydantic models
- core/state_store.py — CRUD for student JSON
- 3 student profiles in data/students/
- Sample work images in data/sample_work/
- prompts/templates.py — all prompt templates
- tests/conftest.py + tests/mock_api_responses.py

## Sprint 1 Build Order

### 1. core/gemma_client.py — API wrapper (Phase 1 Day 1)
Single wrapper for text, multimodal, function calling, thinking mode.
Spec is in IMPLEMENTATION-PLAN.md §4.1.

### 2. schemas/tools.py — Function calling schemas (Phase 1 Day 2)
All JSON schemas for Gemma 4 function calling declarations.
Spec is in IMPLEMENTATION-PLAN.md §4.2.

### 3. agents/base.py — Base agent class (Phase 2)
Shared GemmaClient instance, common _parse_fallback() method.

### 4. agents/vision_reader.py — Agent 1 (Phase 2 Days 4-5)
Multimodal OCR: image → structured JSON via function calling.
KEY TEST: correctly reads Maya's 7/10 math worksheet.

### 5. agents/iep_mapper.py — Agent 2 (Phase 2 Days 6-7)
Maps transcribed work → IEP goals, records trial data.
KEY TEST: maps Maya's math worksheet to Goal G2.

### 6. agents/progress_analyst.py — Agent 3 (Phase 2 Days 8-9)
Thinking mode: trend detection, alerts, progress notes.
KEY TEST: detects Maya's G2 plateau.

### 7. core/pipeline.py — Wire it all together (Phase 2 Day 10)
End-to-end: image → transcription → mapping → analysis.
KEY TEST: full pipeline runs in <30s for one image.
